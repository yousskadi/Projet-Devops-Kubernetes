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
        // stage('Clean stage') {
        //         steps {
        //             sh 'docker system prune -a --volumes -f'
        //             sh 'kubectl delete all --all -n default'
        //             sh 'kubectl delete all --all -n dev'
        //             sh 'kubectl delete all --all -n staging'
        //             sh 'kubectl delete all --all -n prod'
        //         }
        // }

        // stage('Cleanup docker containers and images') {
        //     steps {
        //         script {
                    
        //             def runningContainers = sh(script: 'docker ps', returnStatus: true)
        //             if (runningContainers == 0) {
        //                 echo "No running containers found."
        //             } else {
        //                 sh 'docker stop $(docker ps -aq)'
        //                 sh 'docker rm $(docker ps -aq)'
        //                 sh 'docker rmi -f $(docker images -q)'
        //             }
        //             sh 'docker ps'
        //             sh 'docker images'
        //         }
        //     }
        // }

        // Build docker image
        // stage('Docker image build') {
        //     steps {
        //         script {
        //         sh '''
        //         docker-compose build
        //         sleep 6
        //         '''
        //         }
        //     }
        // }

        // Run the docker image
        // stage('Docker image up') {
        //         steps {
        //             script {
        //             sh '''
        //             docker ps
        //             docker-compose up -d
        //             sleep 10
        //             '''
        //             }
        //         }
        // }


        stage('Image test') {
            steps {
                script {
                    def fastapiStatus = sh(script: 'curl -s -o /dev/null -w "%{http_code}" http://0.0.0.0:5000', returnStdout: true).trim()
                    def pgadminStatus = sh(script: 'curl -s -o /dev/null -w "%{http_code}" http://0.0.0.0:8082', returnStdout: true).trim()

                    echo "Display fastapiStatus: ${fastapiStatus}"
                    echo "Display pgadminStatus: ${pgadminStatus}"
                        
                    if ((fastapiStatus == '200') && (pgadminStatus == '200' || pgadminStatus == '302')) {
                        echo "Fast API and PgAdmin are running fine"
                    } else {
                        error("Fast API or PgAdmin is not working, check pipeline log to see which one failed")
                    }
                }                           
            }
        }   

         stage('Staging deployment') {
            steps {
                script {
                    
                    // curl -i -X POST -H 'Content-Type: application/json' -d '{"name": "TTT", "email": "TTT@email.com","password": "passwordTTT"}' https://www.devops-youss.cloudns.ph
                    // if curl -i -X GET -H 'accept: application/json' https://www.devops-youss.cloudns.ph/users/1 | grep -qF "toto"; then
                    //     echo "La chaîne 'toto' a été trouvée dans la réponse."
                    // else
                    //     echo "La chaîne 'toto' n'a pas été trouvée dans la réponse."
                    // fi'''


                    def endpointCountUsersStatus = sh(script: 'curl -s -o /dev/null -w "%{http_code}" https://www.devops-youss.cloudns.ph/users/count', returnStdout: true).trim()
                    echo "Display endpointCountUsersStatus: ${endpointCountUsersStatus}"

                    if ((endpointCountUsersStatus == '200')) {
                        echo "Endpoint count on users is working fine"
                    } else {
                        error("Endpoint error on users, please check pipeline log to see which one failed")
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


