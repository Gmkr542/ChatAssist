from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape

router = APIRouter()

jinja_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"]),
    cache_size=0,
)

index_template = jinja_env.get_template("index.html")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main ChatLingo interface."""
    return HTMLResponse(index_template.render())
