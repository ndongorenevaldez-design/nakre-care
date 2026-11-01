"""Run with original static server :8001 and Django :8000, using synthetic/local traffic only."""

from pathlib import Path
import json
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

out = Path("test-results/render")
out.mkdir(parents=True, exist_ok=True)
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/usr/bin/chromium", args=["--no-sandbox"]
    )
    for route, name in [("/", "home"), ("/recrutement/", "recruitment")]:
        for width in (375, 1440):
            pair = []
            for kind, port in [("original", 8001), ("django", 8000)]:
                page = browser.new_page(
                    viewport={"width": width, "height": 900}, reduced_motion="reduce"
                )
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                assert page.goto(f"http://127.0.0.1:{port}{route}").status == 200
                for img in page.locator("img").all():
                    img.scroll_into_view_if_needed()
                    page.wait_for_function(
                        "(i)=>i.complete && i.naturalWidth>0", arg=img.element_handle()
                    )
                page.evaluate("scrollTo(0,0)")
                assert page.evaluate(
                    "document.documentElement.scrollWidth <= innerWidth"
                )
                assert page.locator("h1").count() == 1
                assert not errors, errors
                path = out / f"{name}-{width}-{kind}.png"
                page.screenshot(path=str(path), full_page=True)
                pair.append(Image.open(path).convert("RGB").crop((0, 0, width, 900)))
                if kind == "django" and width == 375:
                    page.locator("[data-menu-toggle]").click()
                    assert (
                        page.locator("[data-menu-toggle]").get_attribute(
                            "aria-expanded"
                        )
                        == "true"
                    )
                    page.keyboard.press("Escape")
                    assert (
                        page.locator("[data-menu-toggle]").get_attribute(
                            "aria-expanded"
                        )
                        == "false"
                    )
                page.close()
            diff = ImageChops.difference(*pair)
            changed = sum(1 for pixel in diff.getdata() if pixel != (0, 0, 0))
            ratio = changed / (width * 900)
            # Home first viewport must remain visually identical (contact change is below it).
            if name == "home":
                assert ratio < 0.005, ratio
            montage = Image.new("RGB", (width * 2, 900), "white")
            montage.paste(pair[0], (0, 0))
            montage.paste(pair[1], (width, 0))
            montage.save(out / f"{name}-{width}-comparison.png")
            results.append(
                {"page": name, "width": width, "first_viewport_changed_ratio": ratio}
            )
    page = browser.new_page(
        java_script_enabled=False, viewport={"width": 375, "height": 900}
    )
    page.goto("http://127.0.0.1:8000/")
    assert page.locator("form,input,textarea").count() == 0
    page.get_by_role("link", name="Voir les informations de recrutement").click()
    assert page.url.endswith("/recrutement/")
    browser.close()
(out / "results.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
