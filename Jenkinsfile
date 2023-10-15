pipeline {
environment { // Declaration of environment variables
DOCKER_ID = "vikinghacker"
DOCKER_IMAGE = "fastapi_kubernetes"
DOCKER_TAG = "v.${BUILD_ID}.0" // we will tag our images with the current build in order to increment the value by 1 with each new build
}
agent any // Jenkins will be able to select all available agents

stages {
        stage(' Docker Build') { // docker build image stage
            steps {
                script {
                sh '''
                 docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
                sleep 6
                '''
                }
            }
        }

        stage(' Docker run') { // run container from our builded image
                steps {
                    script {
                    sh '''
                    echo "Cleaning existing container if exist"
                    docker ps -a | grep -i fastapi && docker rm -f fastapi
                    docker run -d -p 5000:5000 --name fastapi $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    sleep 10
                    '''
                    }
                }
        }

        stage('Test Acceptance') { // we launch the curl command to validate that the container responds to the request
            steps {
                    script {
                    sh '''
                    curl -X 'POST' -H 'Content-Type: application/json' -d '{"id": 1, "name": "toto", "email": "toto@email.com","password": "passwordtoto"}' http://52.30.113.35:80
                    if curl -X 'GET' -H 'accept: application/json' http://52.30.113.35:80/users | grep -qF "toto"; then
                        echo "La chaîne 'titi' a été trouvée dans la réponse."
                    else
                        echo "La chaîne 'titi' n'a pas été trouvée dans la réponse."
                    fi  
                    '''
                    }
            }

        }

        stage('Docker Push') { //we pass the built image to our docker hub account
            environment
            {
                DOCKER_PASS = credentials("DOCKER_HUB_PASS") // we retrieve  docker password from secret text called docker_hub_pass saved on jenkins
            }

            steps {
                script {
                sh '''
                docker login -u $DOCKER_ID -p $DOCKER_PASS
                docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                '''
                }
            }
        }

        stage('Dev deployment') {
            environment {
                KUBECONFIG = credentials("config")
                DOCKER_PASS = credentials("DOCKER_HUB_PASS")
            }
            steps {
                script {
                    // install or upgrade the release
                    // upgradeStatus contains the string "DEPLOYED" if deployment succeeded
                    def upgradeStatus = helm(
                        name: 'myapp-release-dev',
                        chart: 'myapp1/',
                        values: ['myapp1/values.yaml', 'myapp1/values-dev.yaml'],
                        namespace: 'dev',
                        wait: true,
                        reuseValues: true
                    )

                    // check if everything is alright after deployment
                    if (upgradeStatus == 'DEPLOYED') {
                        echo 'Helm release upgraded successfully.'
                    } else {
                        echo 'Helm release installed successfully.'
                    }
                }
            }
        }  
    }
}   


