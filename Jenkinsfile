pipeline {
    environment { // Declaration of environment variables
        DOCKER_ID = "vikinghacker"
        DOCKER_IMAGE = "fastapi_kubernetes"
        DOCKER_TAG = "v.${BUILD_ID}.0" // we will tag our images with the current build in order to increment the value by 1 with each new build
        KUBECONFIG = credentials("config")
        DOCKER_PASS = credentials("DOCKER_HUB_PASS")
    }
    agent any // Jenkins will be able to select all available agents

    stages {
        // get rid of unused docker data and volumes and network and so on
        // clean kubernetes cluster
        // docker system prune is for spaces reclaimed only
        stage('Clean stage') {
                steps {
                    sh 'docker system prune -a --volumes -f'
                    sh 'kubectl delete all --all -n default'
                    sh 'kubectl delete all --all -n dev'
                    sh 'kubectl delete all --all -n staging'
                    sh 'kubectl delete all --all -n prod'
                }
        }


        stage('Cleanup docker containers and images') {
            steps {
                script {
                    
                    def runningContainers = sh(script: 'docker ps', returnStatus: true)
                    if (runningContainers == 0) {
                        echo "No running containers found."
                    } else {
                        sh 'docker stop $(docker ps -aq)'
                        sh 'docker rm $(docker ps -aq)'
                        sh 'docker rmi -f $(docker images -q)'
                    }
                    sh 'docker ps'
                    sh 'docker images'
                }
            }
        }



        // stage('Docker Build') {
        //     steps {
        //         script {
        //         sh '''
        //         docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
        //         sleep 6
        //         '''
        //         }
        //     }
        // }

        // stage('Docker run') { // run container from our builded image
        //         steps {
        //             script {
        //             sh '''
        //             docker ps -a | grep -i fastapi && docker rm -f fastapi
        //             docker run -d -p 5000:5000 --name fastapi $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
        //             sleep 10
        //             '''
        //             }
        //         }
        // }

        stage('Docker image build') {
            steps {
                script {
                sh '''
                docker-compose build
                sleep 6
                '''
                }
            }
        }

        stage('Docker image up') { // run container from our builded image
                steps {
                    script {
                    sh '''
                    docker ps
                    docker-compose up -d
                    sleep 10
                    '''
                    }
                }
        }

        stage('Test Acceptance') {
            steps {
                script {
                    sh 'curl -X POST -H "Content-Type: application/json" -d \'{"id": 1, "name": "toto", "email": "toto@email.com", "password": "passwordtoto"}\' http://localhost:80/users'
                    sleep 10  // give time to server
                    
                    // get request to check if toto exists
                    def response = sh(script: 'curl -X GET -H "accept: application/json" http://localhost:80/users', returnStdout: true).trim()
                    
                    if (response.contains("toto")) {
                        echo "The string 'toto' was found in the response."
                    } else {
                        echo "The string 'toto' was not found in the response."
                    }
                }
            }
        }

        // stage('Stop Docker image') {
        //     steps {
        //         script {
        //             sh 'docker-compose down'
        //         }
        //     }
        // }

        // stage('Docker Push') { //we pass the built image to our docker hub account
        //     steps {
        //         script {
        //                 echo 'Performing Docker login'
        //                 sh "docker login -u $DOCKER_ID -p $DOCKER_PASS"
        //                 sh "docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG"
        //         }
        //     }
        // }

        // stage('Local Dev deployment') {
        //     steps {
        //         script {
        //             def valuesYamlPath = 'myapp1/values.yaml'
        //             def valuesDevYamlPath = 'myapp1/values-dev.yaml'
        //             sh """
        //                 sed -i 's/tag:.*/tag: "$DOCKER_TAG"/' $valuesYamlPath
        //                 helm upgrade --install myapp-release-dev myapp1/ --values $valuesYamlPath -f $valuesDevYamlPath -n dev
        //             """
        //         }
        //     }
        // }
    }
}   


