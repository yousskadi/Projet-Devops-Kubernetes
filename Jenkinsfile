pipeline {
    environment { // Declaration of environment variables
        DOCKER_ID = "vikinghacker"
        DOCKER_IMAGE = "fastapi_kubernetes"
        DOCKER_TAG = "v.${BUILD_ID}.0" // we will tag our images with the current build in order to increment the value by 1 with each new build
    }
    agent any // Jenkins will be able to select all available agents

    stages {
        // get rid of unused docker data and volumes and network and so on
        // clean kubernetes cluster
        stage('Clean stage') {
                steps {
                    sh 'docker system prune -a --volumes -f'
                    sh 'kubectl delete all --all -n default'
                }
        }

        stage('Docker Build') {
            steps {
                script {
                sh '''
                docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
                sleep 6
                '''
                }
            }
        }

        stage('Docker run') { // run container from our builded image
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

        stage('Acceptance test') { // we launch the curl command to validate that the container responds to the request
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

        stage('Local Dev deployment') {
            environment {
                KUBECONFIG = credentials("config")
                DOCKER_PASS = credentials("DOCKER_HUB_PASS")
            }
            steps {
                script {
                sh '''
                sed -i "s/tag:.*/tag: \"$DOCKER_TAG\"/" myapp1/values.yaml
                helm upgrade --install myapp-release-dev myapp1/ --values myapp1/values.yaml -f myapp1/values-dev.yaml -n dev
                '''
                }
            }
        }
    }
}   


