pipeline {
    agent any
    environment {
        GIT_TAG_COMMIT = sh(script: 'git describe --tags --always', returnStdout: true).trim()
        GIT_COMMIT_MSG = sh (script: 'git log -1 --pretty=%B ${GIT_COMMIT}', returnStdout: true).trim()
        
        BUILD_TRIGGER_BY_NAME = getBuildUser()

        SERVER_IP_DEPLOY_DEFAULT = credentials('server-ip-deploy-default')
        SERVER_PATH_DELOY_DEFAULT = credentials('server-path-deploy-default')

        TELEGRAM_ENABLE = credentials('telegram-enable')
        TELEGRAM_TOKEN = credentials('telegram-token') 
        TELEGRAM_CHAT_ID = credentials('telegram-chat-id')
    }

    stages {
        stage('Pre-Build') {
            steps {
                script {
                    echo "${currentBuild.changeSets}"
                    if (TELEGRAM_ENABLE == '1') {
                        sendTelegram("[ ${BUILD_TRIGGER_BY_NAME} ][ ${JOB_NAME} ] Build started... 💛💛💛 \nLast commit: ${GIT_COMMIT_MSG}");
                    }
                }
            }
        }
        stage('Setup-ENV') {
            steps {
                script {
                    env.DEPLOY_SERVER_USER = 'jenkins';
                    env.GIT_BRANCH_NAME = getGitBranchName();
                    env.PUSHER = sh (script: 'whoami', returnStdout: true).trim();
                    if (env.GIT_BRANCH_NAME == 'master') {
                        env.PROJECT_DIR = '${SERVER_PATH_DELOY_DEFAULT}COMPILE/api';
                        env.DEPLOY_SERVER_IP = SERVER_IP_DEPLOY_DEFAULT;
                    }
                    if (env.GIT_BRANCH_NAME == 'dev') {
                        echo "TO STEP SET DEV";
                        env.PROJECT_DIR = '${SERVER_PATH_DELOY_DEFAULT}dev/api';
                        env.DEPLOY_SERVER_IP = SERVER_IP_DEPLOY_DEFAULT;
                    }
                    if (env.GIT_BRANCH_NAME == 'sit') {
                        env.PROJECT_DIR = '${SERVER_PATH_DELOY_DEFAULT}sit/api';
                        env.DEPLOY_SERVER_IP = SERVER_IP_DEPLOY_DEFAULT;
                    }
                    if (env.GIT_BRANCH_NAME == 'uat') {
                        env.PROJECT_DIR = '${SERVER_PATH_DELOY_DEFAULT}uat/api';
                        env.DEPLOY_SERVER_IP = SERVER_IP_DEPLOY_DEFAULT;
                    }
                    echo "SETUP ENVIRONMENT SUCCESSFUL";
                }
            }
        }
        stage('Deploy') {
            steps {
                echo "START SSH SERVER";
                echo "START SSH SERVER IP: $DEPLOY_SERVER_IP";
                script {
                    try {
                        if (GIT_BRANCH_NAME == 'master') {
                            sh """ssh -tt $DEPLOY_SERVER_USER@$DEPLOY_SERVER_IP $PROJECT_DIR/compile.sh""";
                        } else {
                            sh """ssh -tt $DEPLOY_SERVER_USER@$DEPLOY_SERVER_IP $PROJECT_DIR/deploy.sh""";
                        }
                    } catch (Exception e) {
                        env.ERROR_MESSAGE = e.getMessage()
                        throw e
                    }
                }
                echo "DONE SSH SERVER";
            }
        }
    }
    post {
        success {
            script {
                if (TELEGRAM_ENABLE == '1') {
                    sendTelegram("[ ${BUILD_TRIGGER_BY_NAME} ][ ${JOB_NAME}] Build finished: Successful 💚💚💚")
                }
            }
        }
        failure {
            script {
                if (TELEGRAM_ENABLE == '1') {
                    def errorMsg = env.ERROR_MESSAGE ?: 'No error message available'
                    sendTelegram("[ ${BUILD_TRIGGER_BY_NAME} ][ ${JOB_NAME} ] Build finished: Failure 💔💔💔 \nErrors: ${errorMsg}")
                }
            }
        }
    }
}

@NonCPS
def getGitBranchName() {
    return scm.branches[0].name.split("/")[1]
}

def sendTelegram(message) {
    def msgEncode = java.net.URLEncoder.encode(message, "UTF-8")
    sh """
        curl -s -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage \
            -d chat_id=${TELEGRAM_CHAT_ID} \
            -d text="${msgEncode}"
    """
}

@NonCPS
def getBuildUser() {
    // [_class:hudson.model.Cause$UserIdCause, shortDescription:Started by user ADMIN, userId:admin, userName:ADMIN]
    return "${currentBuild.getBuildCauses()[0].userId} : ${currentBuild.getBuildCauses()[0].userName}"
}
