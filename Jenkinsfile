pipeline {
    agent any
    environment {
        GIT_TAG_COMMIT = sh(script: 'git describe --tags --always', returnStdout: true).trim()

        TELEGRAM_TOKEN = credentials('telegram-token') 
        TELEGRAM_CHAT_ID = credentials('telegram-chat-id')
        TEXT_PRE_BUILD = "Jenkins is building ${JOB_NAME}"
        TEXT_SUCCESS_BUILD = "${JOB_NAME} is Success"
        TEXT_FAILURE_BUILD = "${JOB_NAME} is Failure"
    }

    stages {
        stage('Pre-Build') {
            steps {
                script {
                    sh '''
                        curl -s -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage \
                            -d chat_id=${TELEGRAM_CHAT_ID} \
                            -d text="${TEXT_PRE_BUILD}"
                    '''
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
                        env.PROJECT_DIR = '/home/jenkins/COMPILE/API';
                        env.DEPLOY_SERVER_IP = '192.168.0.111';
                    }
                    if (env.GIT_BRANCH_NAME == 'dev') {
                        echo "TO STEP SET DEV";
                        env.PROJECT_DIR = '/home/jenkins/dev/api';
                        env.DEPLOY_SERVER_IP = '192.168.0.111';
                    }
                    if (env.GIT_BRANCH_NAME == 'sit') {
                        env.PROJECT_DIR = '/home/jenkins/sit/api';
                        env.DEPLOY_SERVER_IP = '192.168.0.111';
                    }
                    if (env.GIT_BRANCH_NAME == 'uat') {
                        env.PROJECT_DIR = '/home/jenkins/uat/api';
                        env.DEPLOY_SERVER_IP = '192.168.0.111';
                    }
                    echo "SETUP ENVIRONMENT SUCCESSFUL";
                }
            }
        }
        stage('Deploy') {
            steps {
                echo "START SSH SERVER";
                script {
                    if (GIT_BRANCH_NAME == 'master') {
                        sh """ssh -tt $DEPLOY_SERVER_USER@$DEPLOY_SERVER_IP $PROJECT_DIR/compile.sh""";
                    } else {
                        sh """ssh -tt $DEPLOY_SERVER_USER@$DEPLOY_SERVER_IP $PROJECT_DIR/deploy.sh""";
                    }
                }
                echo "DONE SSH SERVER";
            }
        }
    }
    post {
        success {
            script {
                sh """
                    curl -s -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage \
                    -d chat_id=${TELEGRAM_CHAT_ID} \
                    -d text="Build finished: SUCCESSFUL"
                """
            }
        }
        failure {
            script {
                sh """
                    curl -s -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage \
                    -d chat_id=${TELEGRAM_CHAT_ID} \
                    -d text="Build finished: FAILURE"
                """
            }
        }
    }
}

@NonCPS
def getGitBranchName() {
    return scm.branches[0].name.split("/")[1]
}

