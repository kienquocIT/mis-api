pipeline {
    agent any
    environment {
        GIT_TAG_COMMIT = sh(script: 'git describe --tags --always', returnStdout: true).trim()
    }

    stages {
        stage('Setup-ENV') {
            steps {
                script {
                    env.DEPLOY_SERVER_USER = 'jenkins'
                    env.GIT_BRANCH_NAME = getGitBranchName();
                    env.PUSHER = sh (script: 'whoami', returnStdout: true).trim();
                    if (GIT_BRANCH_NAME == 'master') {
                        env.PROJECT_DIR = '/home/jenkins/api_mis';
                        env.PROJECT_BUILD_DIR = env.PROJECT_DIR + '/src' + '/';
                        env.DEPLOY_SERVER_IP = '192.168.0.111';
                    if (GIT_BRANCH_NAME == 'dev') {
                        env.PROJECT_DIR = '/home/jenkins/dev/api';
                        env.PROJECT_BUILD_DIR = env.PROJECT_DIR;
                        env.DEPLOY_SERVER_IP = '192.168.0.111';
                    if (GIT_BRANCH_NAME == 'sit') {
                        env.PROJECT_DIR = '/home/jenkins/sit/api';
                        env.PROJECT_BUILD_DIR = env.PROJECT_DIR;
                        env.DEPLOY_SERVER_IP = '192.168.0.111';
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                echo "START SSH SERVER"
                script {
                    sh """ssh -tt $DEPLOY_SERVER_USER@$DEPLOY_SERVER_IP $PROJECT_DIR/deploy.sh"""
                }
                echo "DONE SSH SERVER"
            }
        }
    }
}

@NonCPS
def getGitBranchName() {
    return scm.branches[0].name.split("/")[1]
}

