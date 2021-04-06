function assertPiveNamespace() {
    if(window.pive == undefined) {
        window.pive = {};
    }
}

function addChartVersion(name, version, clazz) {
    let o = window.pive;
    if(o[name] == undefined) {
        o[name] = {};
    }
    if(o[name][version] == undefined) {
        o[name][version] = clazz
    } else {
        //already defined, raise exception?
    }
}

assertPiveNamespace();
window.pive.assertPiveNamespace = assertPiveNamespace;
window.pive.addChartVersion = addChartVersion;