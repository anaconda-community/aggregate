arch_support = {
    "linux-64": False,
    "linux-ppc64le": False,
    "linux-aarch64": False,
    "linux-s390x": False,
    "osx-64": False,
    "osx-arm64": False,
    "win-64": False,
}

arch_selector_template = {
    "win": False,
    "osx": False,
    "x86_64": False,
    "arm64": False,
    "linux": False,
    "linux64": False,
    "s390x": False,
    "aarch64": False,
    "ppc64le": False,
}


class arch_selectors:
    linux_64 = arch_selector_template.copy()
    linux_64["linux"] = True
    linux_64["x86_64"] = True
    linux_64["linux64"] = True

    linux_ppc64le = arch_selector_template.copy()
    linux_ppc64le["linux"] = True
    linux_ppc64le["ppc64le"] = True

    linux_aarch64 = arch_selector_template.copy()
    linux_aarch64["linux"] = True
    linux_aarch64["aarch64"] = True

    linux_s390x = arch_selector_template.copy()
    linux_s390x["linux"] = True
    linux_s390x["s390x"] = True

    osx_64 = arch_selector_template.copy()
    osx_64["osx"] = True
    osx_64["x86_64"] = True

    osx_arm64 = arch_selector_template.copy()
    osx_arm64["osx"] = True
    osx_arm64["arm64"] = True

    win = arch_selector_template.copy()
    win["win"] = True
    win["x86_64"] = True


archSelectorCombs = {
    "linux-64": arch_selectors.linux_64,
    "linux-ppc64le": arch_selectors.linux_ppc64le,
    "linux-aarch64": arch_selectors.linux_aarch64,
    "linux-s390x": arch_selectors.linux_s390x,
    "osx-64": arch_selectors.osx_64,
    "osx-arm64": arch_selectors.osx_arm64,
    "win-64": arch_selectors.win,
}


def evaluate_arch_selector(archs2check, expression):
    # archs2check as a list: ['win','linux-64','osx-arm64']
    # expression as a string: 'linux or (osx and x86_64)'
    archSupportDep = arch_support.copy()
    for arch in archs2check:
        if not expression:
            archSupportDep[arch] = True
        else:
            try:
                result = eval(expression, {}, archSelectorCombs[arch])
                if result:
                    archSupportDep[arch] = True
            except:
                archSupportDep[arch] = True

    return archSupportDep
