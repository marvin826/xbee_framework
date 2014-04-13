
def load_module(module, logger):

    # make a fully-qualified module name by
    # appending the package name
    fqmn = "xbeeframework." + module

    try:
        mod = __import__(fqmn)
        class_ = getattr(mod, module) 
        return getattr(class_, module)

    except Exception, e:
        logMessage = "load_module ERROR:" + \
            str(e)
        logger.critical(logMessage)