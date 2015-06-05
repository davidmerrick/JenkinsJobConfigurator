import xml.etree.ElementTree as ET

class JenkinsJobConfigurator:
    """Configures a Jenkins job. Initialize with Jenkins config as an ElementTree."""

    def __init__(self, jobTree):
        self.__jobTree = jobTree

    def __getProperties(self):
        return self.__jobTree.find("properties")

    def __getBuilders(self):
        return self.__jobTree.find("builders")

    def __getPublishers(self):
        return self.__jobTree.find("publishers")

    # Todo: what if hudson.model.ParametersDefinitionProperty is None?
    def __getParameterDefinitions(self):
        properties = self.__getProperties()
        return properties.find("hudson.model.ParametersDefinitionProperty").find("parameterDefinitions")

    def __createParameterDefinitionProperty(self):
        newProperty = ET.Element("hudson.model.ParametersDefinitionProperty")
        parameterDefinitions = ET.Element("parameterDefinitions")
        newProperty.append(parameterDefinitions)
        return newProperty

    def __createStringParam(self, name, description, default_value):
        param = ET.Element('hudson.model.StringParameterDefinition')
        paramName = ET.SubElement(param, 'name')
        paramName.text = name
        paramDescription = ET.SubElement(param, 'description')
        paramDescription.text = description
        paramDefaultValue = ET.SubElement(param, 'defaultValue')
        paramDefaultValue.text = default_value
        return param

    def __createShellBuildAction(self, command):
        shellBuildAction = ET.Element('hudson.tasks.Shell')
        commandElement = ET.SubElement(shellBuildAction, "command")
        commandElement.text = command
        return shellBuildAction

    def __createPostBuildScriptElement(self, script):
        postBuildScript = ET.Element('org.jenkinsci.plugins.postbuildscript.PostBuildScript')
        scriptFileList = ET.SubElement(postBuildScript, "genericScriptFileList")

        genericScript = ET.Element("org.jenkinsci.plugins.postbuildscript.GenericScript")
        filePath = ET.SubElement(genericScript, "filePath")
        filePath.text = script

        scriptOnlyIfSuccess = ET.SubElement(postBuildScript, "scriptOnlyIfSuccess")
        scriptOnlyIfSuccess.text = "true"

        scriptOnlyIfFailure = ET.SubElement(postBuildScript, "scriptOnlyIfFailure")
        scriptOnlyIfFailure.text = "false"

        scriptFileList.append(genericScript)
        return postBuildScript

    def __removeChildren(self, parent):
        for child in parent.findall("*"):
            parent.remove(child)

    def removeAllParams(self):
        properties = self.__getProperties()
        parameterDefinitionsProperty = properties.find("hudson.model.ParametersDefinitionProperty")
        if parameterDefinitionsProperty is not None:
            properties.remove(parameterDefinitionsProperty)
        parameterDefinitionsProperty = self.__createParameterDefinitionProperty()
        properties.append(parameterDefinitionsProperty)

    def addParam(self, name, description, defaultValue):
        param = self.__createStringParam(name, description, defaultValue)
        jobParameters = self.__getParameterDefinitions()
        jobParameters.append(param)

    def removeBuildActions(self):
        builders = self.__getBuilders()
        self.__removeChildren(builders)

    def removePublishers(self):
        publishers = self.__getPublishers()
        self.__removeChildren(publishers)

    def addShellBuildAction(self, command):
        builders = self.__getBuilders()
        shellBuildAction = self.__createShellBuildAction(command)
        builders.append(shellBuildAction)

    def addPostBuildScript(self, script):
        postBuildScriptElement = self.__createPostBuildScriptElement(script)
        publishers = self.__getPublishers()
        publishers.append(postBuildScriptElement)

    def removePostBuildScripts(self):
        publishers = self.__getPublishers()
        postBuildScripts = publishers.find('org.jenkinsci.plugins.postbuildscript.PostBuildScript')
        publishers.remove(postBuildScripts)

    def getUpdatedConfig(self):
        return self.__jobTree
