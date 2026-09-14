"""Headless browser regression for the single-file drone game.

Run with: python3 tests/test_game.py
Requires the existing local server at http://127.0.0.1:8746/.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8746/"
OUT = Path("/Users/yquanloo/Documents/my-agent/playwright-to-delete/drone-upgrade")
OUT.mkdir(parents=True, exist_ok=True)

def wait_ready(page, completed_onboarding=True):
    if completed_onboarding:
        page.add_init_script("""localStorage.setItem('drone-club-v2', JSON.stringify({
          onboardingComplete: true, control: 'assist', sound: false, best: {}
        }))""")
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_function("window.__gameReady === true", timeout=15000)

def wait_started(page):
    page.wait_for_function("window.__debugState.started && window.__debugState.countdown <= 0", timeout=20000)

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        # A first-time visitor bypasses the menu and enters the five-ring trial.
        first = browser.new_page(viewport={"width": 1440, "height": 900})
        wait_ready(first, completed_onboarding=False)
        first.wait_for_function("window.__debugState.started && window.__debugState.practice")
        assert first.locator("#start-screen").is_hidden()
        first.close()
        for name, width, height, mobile in (("desktop", 1440, 900, False), ("mobile844", 844, 390, True), ("mobile667", 667, 375, True)):
            page = browser.new_page(viewport={"width": width, "height": height}, is_mobile=mobile, has_touch=mobile)
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            wait_ready(page)
            page.screenshot(path=str(OUT / f"{name}-menu-final.png"))
            layout = page.evaluate("""() => ({inner:[innerWidth,innerHeight], scroll:[document.documentElement.scrollWidth,document.documentElement.scrollHeight], ready:window.__gameReady})""")
            assert layout["scroll"] == layout["inner"], (name, layout)
            page.locator("#practice-btn").click()
            page.wait_for_function("window.__debugState.started")
            countdown = page.evaluate("() => window.__debugState.countdown")
            assert countdown > 0
            page.screenshot(path=str(OUT / f"{name}-countdown-final.png"))
            wait_started(page)
            page.screenshot(path=str(OUT / f"{name}-practice-final.png"))
            # Pause must freeze simulation time and release all controls.
            page.locator("#pause-btn").click()
            frozen = page.evaluate("() => ({time:window.__debugState.matchTime, elapsed:window.__debugState.elapsed, pos:window.__debugState.player.pos.toArray()})")
            page.wait_for_timeout(700)
            frozen2 = page.evaluate("() => ({time:window.__debugState.matchTime, elapsed:window.__debugState.elapsed, pos:window.__debugState.player.pos.toArray(), paused:window.__debugState.paused, input:window.__debugGame.flightInput()})")
            assert frozen2["paused"] and frozen2["time"] == frozen["time"] and frozen2["elapsed"] == frozen["elapsed"] and frozen2["pos"] == frozen["pos"]
            page.locator("#resume-btn").click()
            page.wait_for_function("!window.__debugState.paused")
            if mobile:
                assert page.evaluate("matchMedia('(pointer:coarse)').matches && navigator.maxTouchPoints > 0")
                # Real emulated touch events: two thumbs, capture outside the stick,
                # then cancellation. A mouse drag does not exercise this contract.
                box = page.locator("#stick-left").bounding_box()
                cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                boost = page.locator("#boost-btn").bounding_box()
                cdp = page.context.new_cdp_session(page)
                finger = {"x": cx, "y": cy-35, "id": 1}
                other = {"x": boost["x"]+boost["width"]/2, "y": boost["y"]+boost["height"]/2, "id": 2}
                cdp.send("Input.dispatchTouchEvent", {"type":"touchStart", "touchPoints":[finger]})
                cdp.send("Input.dispatchTouchEvent", {"type":"touchStart", "touchPoints":[finger, other]})
                touch_input = page.evaluate("() => window.__debugGame.flightInput()")
                assert touch_input["pitch"] > 0.1, touch_input
                assert page.evaluate("__debugState.boosting")
                z = page.evaluate("__debugState.player.pos.z")
                page.wait_for_function("__debugState.player.pos.z < " + str(z-.2))
                finger["y"] = box["y"]-15
                cdp.send("Input.dispatchTouchEvent", {"type":"touchMove", "touchPoints":[finger,other]})
                assert page.evaluate("__debugGame.flightInput().pitch > .9")
                cdp.send("Input.dispatchTouchEvent", {"type":"touchCancel", "touchPoints":[]})
                page.wait_for_function("__debugGame.flightInput().pitch === 0 && !__debugState.boosting")
                print(name, "two-thumb touch/movement/capture/cancel OK")
            assert not errors, errors
            print(name, "ready/layout/countdown/pause OK", layout, countdown, frozen2)
            page.close()

        # Desktop real keyboard progression + deterministic gate crossing contract.
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        final_errors=[]
        page.on("pageerror", lambda e: final_errors.append(str(e)))
        wait_ready(page)
        page.locator('.diff-btn[data-diff="easy"]').click()
        wait_started(page)
        before = page.evaluate("() => ({idx:__debugState.player.gateIndex, pos:__debugState.player.pos.toArray()})")
        page.keyboard.down("w")
        page.wait_for_function("window.__debugState.gates >= 1", timeout=20000)
        page.keyboard.up("w")
        after = page.evaluate("() => ({idx:__debugState.player.gateIndex, gates:__debugState.gates, pos:__debugState.player.pos.toArray()})")
        assert after["gates"] >= 1 and after["idx"] != before["idx"], (before, after)
        crossing = page.evaluate("""() => {
          const g=__debugCourse.gates[0], d=__debugState.player;
          const origin=d.pos.clone().set(0,0,0), axis=d.pos.clone().set(1,0,0);
          g.localToWorld(origin); g.localToWorld(axis); axis.sub(origin).normalize();
          const old=d.pos.clone(), oldPrev=d.prevPos.clone();
          const setLocal=(x,y,z)=>{let v=d.pos.clone().set(x,y,z);g.localToWorld(v);return v};
          d.prevPos.copy(setLocal(-5,0,0)); d.pos.copy(setLocal(5,0,0)); const forward=__debugGame.checkGoalCrossing(d,g);
          d.prevPos.copy(setLocal(5,0,0)); d.pos.copy(setLocal(-5,0,0)); const reverse=__debugGame.checkGoalCrossing(d,g);
          d.prevPos.copy(setLocal(-5,4,0)); d.pos.copy(setLocal(5,4,0)); const outside=__debugGame.checkGoalCrossing(d,g);
          d.prevPos.copy(setLocal(-5,3,0)); d.pos.copy(setLocal(5,-3,0)); const swept=__debugGame.checkGoalCrossing(d,g);
          d.pos.copy(old); d.prevPos.copy(oldPrev); return {forward,reverse,outside,swept};
        }""")
        assert crossing == {"forward": True, "reverse": True, "outside": False, "swept": True}, crossing
        print("desktop keyboard/crossing OK", before, after, crossing)

        # Quiz starts with a thinking phase: no answer ring and no target marker.
        page.locator("#pause-btn").click(); page.locator("#pause-menu-btn").click()
        page.locator('[data-mode="quiz"]').click(); page.locator('.diff-btn[data-diff="easy"]').click(); wait_started(page)
        quiz = page.evaluate("() => ({mode:__debugState.mode, phase:__debugQuiz.phase, props:__debugQuiz.props.length, active:__debugQuiz.active, target:__debugGame.currentTarget()})")
        assert quiz == {"mode": "quiz", "phase": "think", "props": 0, "active": True, "target": None}, quiz
        page.evaluate("__debugGame.revealAnswerRings()")
        quiz = page.evaluate("() => ({phase:__debugQuiz.phase, props:__debugQuiz.props.length, directions:__debugQuiz.props.map(p=>p.letter), target:__debugGame.currentTarget(), radar:document.querySelector('#answer-radar').innerText, markerHidden:document.querySelector('#target-marker').hidden})")
        assert quiz["phase"] == "answer" and quiz["props"] == 4 and quiz["target"] is None and quiz["markerHidden"], quiz
        assert quiz["directions"] == list("ABCD") and "X " not in quiz["radar"], quiz
        print("quiz thinking/reveal/no-target/radar OK", quiz)
        # Keep the real scoring flow while positioning at a known gate. This
        # isolates correct/wrong answers from the separate keyboard flight test.
        page.evaluate("__debugState.countdown=0; __debugState.ais.forEach(a=>a.hitCooldown=100)")
        def cross_quiz(correct):
            page.evaluate("""correct => {
              const p=__debugQuiz.props.find(p=>p.correct===correct), d=__debugState.player;
              const n=p.group.userData.normal;
              d.pos.copy(p.group.position).addScaledVector(n,-.12); d.prevPos.copy(d.pos);
              d.vel.copy(n).multiplyScalar(8); d.heading=Math.atan2(-n.x,-n.z); d.hitCooldown=0;
            }""", correct)
            page.keyboard.down('w')
        cross_quiz(False)
        page.wait_for_function("__debugState.learning.wrong === 1")
        page.keyboard.up('w')
        assert page.evaluate("__debugQuiz.active && __debugQuiz.props.length === 3 && __debugState.scores.player === 0")
        cross_quiz(True)
        page.wait_for_function("__debugState.learning.correct === 1")
        page.keyboard.up('w')
        assert page.evaluate("!__debugQuiz.active && __debugState.scores.player === 1")
        page.evaluate("__debugState.matchTime=.001")
        page.wait_for_function("__debugState.matchOver")
        assert page.locator('#end-screen').is_visible()
        assert page.evaluate("JSON.parse(localStorage.getItem('drone-club-v2')).best['quiz:easy:assist'] === 1")
        page.locator('#restart-btn').click()
        assert page.evaluate("!__debugState.matchOver && __debugState.scores.player === 0 && __debugState.matchTime === 90")
        print('quiz wrong/correct/timeout/storage/restart OK')
        page.locator('#pause-btn').click(); page.locator('#pause-menu-btn').click()
        page.locator('#practice-btn').click(); wait_started(page)
        for gate in range(5):
            page.evaluate("""() => {
              const g=__debugCourse.gates[__debugState.player.gateIndex], d=__debugState.player, n=g.userData.normal;
              d.pos.copy(g.position).addScaledVector(n,-.12); d.prevPos.copy(d.pos);
              d.vel.copy(n).multiplyScalar(8); d.heading=Math.atan2(-n.x,-n.z);
            }""")
            page.keyboard.down('w'); page.wait_for_function('__debugState.gates > '+str(gate)); page.keyboard.up('w')
        assert page.evaluate('__debugState.matchOver && __debugState.gates === 5')
        assert page.locator('#restart-btn').inner_text() == '去轻松飞 →'
        page.locator('#restart-btn').click()
        assert page.evaluate("!__debugState.practice && __debugState.mode === 'race' && __debugState.difficulty === 'easy'")
        print('practice 5 gates/results/next race OK')
        assert not final_errors, final_errors
        browser.close()

if __name__ == "__main__":
    main()
