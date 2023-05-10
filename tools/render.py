from jinja2 import Environment, FileSystemLoader
from vendor import UndefinedNeverFail


def ignore_undefined(undefined: set) -> set:
    assert isinstance(undefined, set)

    ignore = {
        "PYTHON",
        "python",
        "environ",
        "target_platform",
        "compiler",
        "cdt",
        "pin_subpackage",
        "pin_compatible",
    }
    return undefined - ignore


def render_template(template, data, no_output=False):
    """
    Render the meta.yaml using Jinja2: return YAML data
    This uses conda-build's jinja context to prevent failures for special conda-build
    variables like {{ compiler('c') }} and any other undefined jinja expansions
    """

    if not template:
        return ""

    try:
        rendered = template.render(data)
    except TypeError:
        print(f"NoneType template")
        return ""

    return rendered


def load_template_string(data, env_string, no_output=False):
    env = Environment(undefined=UndefinedNeverFail)
    template = env.from_string(env_string)
    return render_template(template, data, no_output=no_output)
