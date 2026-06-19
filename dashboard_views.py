import json
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from userspermissionsystem.dashboard import ai_assistant_reply, get_dashboard_stats

DOCS_DIR = Path(__file__).resolve().parent / "docs"
STAFF_LOGIN = getattr(settings, "LOGIN_URL", "/admin/login/")


@staff_member_required(login_url=STAFF_LOGIN)
def ai_dashboard(request):
    stats = get_dashboard_stats()
    return render(
        request,
        "userspermissionsystem/dashboard.html",
        {
            "stats": stats,
            "page_title": "AI Permission Dashboard",
        },
    )


@staff_member_required(login_url=STAFF_LOGIN)
def documentation(request):
    doc_name = (request.GET.get("page") or "index").strip().lower()
    allowed = {
        "index": "index.md",
        "installation": "installation.md",
        "architecture": "architecture.md",
        "platforms": "platforms.md",
        "plugins": "plugins.md",
        "roles": "roles.md",
        "api": "api.md",
    }
    filename = allowed.get(doc_name, "index.md")
    doc_path = DOCS_DIR / filename
    content = doc_path.read_text(encoding="utf-8") if doc_path.exists() else "# Not found"

    return render(
        request,
        "userspermissionsystem/documentation.html",
        {
            "doc_name": doc_name,
            "doc_content": content,
            "doc_nav": list(allowed.keys()),
            "page_title": "Documentation",
        },
    )


@staff_member_required(login_url=STAFF_LOGIN)
@require_POST
def ai_assistant_api(request):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        body = {}
    question = body.get("question", "")
    return JsonResponse({"answer": ai_assistant_reply(question)})


@staff_member_required(login_url=STAFF_LOGIN)
@require_GET
def ai_assistant_api_get(request):
    question = request.GET.get("q", "")
    return JsonResponse({"answer": ai_assistant_reply(question)})
