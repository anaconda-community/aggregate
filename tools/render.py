import re
import jinja2
import yaml
import contextlib


# Pyyaml configuration
try:
    loader = yaml.CLoader
except:
    loader = yaml.Loader


@contextlib.contextmanager
def _stringify_numbers():
    # ensure that numbers are not interpreted as ints or floats.  That trips up versions
    #     with trailing zeros.
    implicit_resolver_backup = loader.yaml_implicit_resolvers.copy()
    for ch in list("0123456789"):
        if ch in loader.yaml_implicit_resolvers:
            del loader.yaml_implicit_resolvers[ch]
    yield
    for ch in list("0123456789"):
        if ch in implicit_resolver_backup:
            loader.yaml_implicit_resolvers[ch] = implicit_resolver_backup[ch]


# Jinja configuration
class _JinjaSilentUndefined(jinja2.Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        class EmptyString(str):
            def __call__(self, *args, **kwargs):
                return ""

        return EmptyString()

    __add__ = (
        __radd__
    ) = (
        __mul__
    ) = (
        __rmul__
    ) = (
        __div__
    ) = (
        __rdiv__
    ) = (
        __truediv__
    ) = (
        __rtruediv__
    ) = (
        __floordiv__
    ) = (
        __rfloordiv__
    ) = (
        __mod__
    ) = (
        __rmod__
    ) = (
        __pos__
    ) = (
        __neg__
    ) = (
        __call__
    ) = (
        __getitem__
    ) = (
        __lt__
    ) = (
        __le__
    ) = (
        __gt__
    ) = (
        __ge__
    ) = (
        __int__
    ) = __float__ = __complex__ = __pow__ = __rpow__ = _fail_with_undefined_error


_jinja_silent_undef = jinja2.Environment(undefined=_JinjaSilentUndefined)


def _apply_selector(data: str, selector_dict: dict) -> list[str]:
    """Apply selectors # [...]

    Args:
        data (str): Raw meta yaml string
        selector_dict (dict): Selector configuration.

    Returns:
        list[str]: meta yaml filtered based on selectors, as a list of string.
    """
    updated_data = []
    for line in data.splitlines():
        if (match := re.search(r"(\s*)[^#].*(#\s*\[([^\]]*)\].*)", line)) is not None:
            cond_str = match.group(3)
            try:
                if not eval(cond_str, None, selector_dict):
                    line = f"{match.group(1)}"
                else:
                    line = line.replace(
                        match.group(2), ""
                    )  # <-- comments sometimes causes trouble in jinja
            except Exception:
                continue
        updated_data.append(line)
    return "\n".join(updated_data)


def _get_template(meta_yaml, selector_dict):
    """Create a Jinja2 template from the current raw recipe"""
    # This function exists because the template cannot be pickled.
    # Storing it means the recipe cannot be pickled, which in turn
    # means we cannot pass it to ProcessExecutors.
    meta_yaml_selectors_applied = _apply_selector(meta_yaml, selector_dict)
    return _jinja_silent_undef.from_string(meta_yaml_selectors_applied)


def render(meta_yaml, selector_dict):
    #: Variables to pass to Jinja when rendering recipe
    def expand_compiler(lang):
        compiler = selector_dict.get(f"{lang}_compiler", None)
        if not compiler:
            return compiler
        else:
            return f"{compiler}_{selector_dict.get('target_platform', 'linux-64')}"

    JINJA_VARS = {
        "unix": selector_dict.get("unix", False),
        "win": selector_dict.get("win", False),
        "PYTHON": selector_dict.get(
            "PYTHON",
            "%PYTHON%" if selector_dict.get("win", False) else "${PYTHON}",
        ),
        "py": int(selector_dict.get("py", "39")),
        "py3k": selector_dict.get("py3k", "0") == "1",
        "py2k": selector_dict.get("py3k", "0") == "0",
        "build_platform": selector_dict.get("target_platform", "linux-64"),
        "target_platform": selector_dict.get("target_platform", "linux-64"),
        "ctng_target_platform": selector_dict.get("target_platform", "linux-64"),
        "cross_target_platform": selector_dict.get("target_platform", "linux-64"),
        "ctng_gcc": selector_dict.get("c_compiler_version", "7.3.0"),
        "ctng_binutils": selector_dict.get("c_compiler_version", "2.35"),
        "numpy": selector_dict.get("numpy", "1.16"),
        "np": selector_dict.get("np", "116"),
        "pl": selector_dict.get("pl", "5"),
        "lua": selector_dict.get("lua", "5"),
        "luajit": selector_dict.get("lua", "5")[0] == "2",
        "linux64": selector_dict.get("linux-64", "0") == "1",
        "aarch64": selector_dict.get("aarch64", "0") == "1",
        "ppcle64": selector_dict.get("ppcle64", "0") == "1",
        "cran_mirror": "https://cloud.r-project.org",
        "compiler": expand_compiler,
        "pin_compatible": lambda x, max_pin=None, min_pin=None, lower_bound=None, upper_bound=None: f"{x}",
        "pin_subpackage": lambda x, max_pin=None, min_pin=None, exact=False: f"{x}",
        "cdt": lambda x: f"{x}-cos6-x86_64",
        "os.environ.get": lambda name, default="": "",
        "ccache": lambda name, method="": "ccache",
    }
    yaml_text = _get_template(meta_yaml, selector_dict).render(JINJA_VARS)

    with _stringify_numbers():
        return yaml.load(
            yaml_text.replace("\t", " ").replace("%", " "), Loader=loader
        )

