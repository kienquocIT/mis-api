pipeline {
    agent any
    environment {
        GIT_TAG_COMMIT = sh(script: 'git describe --tags --always', returnStdout: true).trim()
    }

    stages {
        stage('Setup-ENV') {
            steps {
                script {
                    echo "SETUP ENVIRONMENT STARTED";
                    env.DEPLOY_SERVER_USER = 'jenkins';
                    echo "DONE: DEPLOY_SERVER_USER";
                    env.GIT_BRANCH_NAME = getGitBranchName();
                    echo "DONE: GIT_BRANCH_NAME";
                    env.PUSHER = sh (script: 'whoami', returnStdout: true).trim();
                    echo "DONE: PUSHER";
                    if (env.GIT_BRANCH_NAME == 'master') {
                        env.PROJECT_DIR = '/home/jenkins/api_mis';
                        env.DEPLOY_SERVER_IP = '192.168.0.111';
                    }
                    if (env.GIT_BRANCH_NAME == 'dev') {
                        echo "TO STEP SET DEV";
                        env.PROJECT_DIR = '/home/jenkins/dev/api';
                        env.DEPLOY_SERVER_IP = '192.168.0.111';
                    }
                    if (env.GIT_BRANCH_NAME == 'sit') {
                        env.PROJECT_DIR = '/home/jenkins/dev/api';
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
                    sh """ssh -tt $DEPLOY_SERVER_USER@$DEPLOY_SERVER_IP $PROJECT_DIR/deploy.sh""";
                }
                echo "DONE SSH SERVER";
            }
        }
    }
}

@NonCPS
def getGitBranchName() {
    println "getGitBranchName started..."
    def branch_tmp = scm.branches
    println "${branch_tmp}"
    return scm.branches[0].name.split("/")[1]
}

