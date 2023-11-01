pipeline {
    environment { // Declaration of environment variables
    DOCKER_ID = "ykadi" // replace this with your docker-id
    DOCKER_IMAGE = "datascientestapi"
    DOCKER_TAG = "v.${BUILD_ID}.0" // we will tag our images with the current build in order to increment the value by 1 with each new build
    KUBECONFIG = credentials("EKS-config") // we retrieve  kubeconfig from secret file called config saved on jenkins
    DOCKER_PASS = credentials("DOCKER_HUB_PASS")
    AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = "eu-west-3"
}

agent any 
    stages {
        stage('Cleanup docker containers and images') {
            steps {
                script {
                    
                    def runningContainers = sh(script: 'docker ps', returnStatus: true)
                    if (runningContainers == 0) {
                        echo "No running containers found."
                    } else {
                        sh 'docker system prune -a --volumes -f'
                        sh 'docker stop $(docker ps -aq)'
                        sh 'docker rm $(docker ps -aq)'
                        sh 'docker rmi -f $(docker images -q)'
                    }
                    sh 'docker ps'
                    sh 'docker images'
                }
            }
        }

        // Build docker image
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

        // Run the docker image
        stage('Docker image up') {
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

        stage('Build and tag docker image for dockerhub') {
            steps {
                script {
                sh '''
                docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
                sleep 6
                '''
                }
            }
        }
       
      /*  stage('Image test') {
            steps {
                script {
                    def fastapiStatus = sh(script: 'curl -s -o /dev/null -w "%{http_code}" http://0.0.0.0:5000', returnStatus: true)
                    def pdagminStatus = sh(script: 'curl -s -o /dev/null -w "%{http_code}" http://0.0.0.0:8082', returnStatus: true)

                    //if (fastapiStatus == 0 && pdagminStatus == 0 || pdagminStatus == 302 ) {
                    if (pdagminStatus == "302" ) {
                        echo "Fast api and pdagmin are running fine"
                        
                    } else {
                        error("Fast api or pgadmin is not working, check pipeline log to see which one failed")
                    }
                }
            }
        }
    */
        // Push the docker image built on dockerhub
        stage('Docker Push') { 
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
            steps {
                script {
                    sh '''
                    echo "Installation Ingress-controller Nginx"
                    helm upgrade --install ingress-nginx ingress-nginx \
                    --repo https://kubernetes.github.io/ingress-nginx \
                    --namespace ingress-nginx --create-namespace     
                    sleep 10

                    echo "Installation Cert-Manager"
                    helm upgrade --install cert-manager cert-manager \
                    --repo https://charts.jetstack.io \
                    --create-namespace --namespace cert-manager \
                    --set installCRDs=true
                    sleep 10
                        
                    echo "Installation Projet Devops 2023"
                    sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" myapp1/values.yaml
                    helm upgrade --install myapp-release-dev myapp1/ --values myapp1/values.yaml -f myapp1/values-dev.yaml -n dev --create-namespace
                        
                    echo "Installation stack Prometheus-Grafana"
                    helm upgrade --install kube-prometheus-stack kube-prometheus-stack \
                    --namespace kube-prometheus-stack --create-namespace \
                    --repo https://prometheus-community.github.io/helm-charts
                    '''
                }
            }           
        }

        stage('Staging deployment') {
            steps {
                script {
                    sh '''
                    curl -i -i 'POST' -H 'Content-Type: application/json' -d '{"id": 1, "name": "toto", "email": "toto@email.com","password": "passwordtoto"}' https://www.devops-youss.cloudns.ph
                    if curl -i 'GET' -H 'accept: application/json' https://www.devops-youss.cloudns.ph/users | grep -qF "toto"; then
                        echo "La chaîne 'toto' a été trouvée dans la réponse."
                    else
                        echo "La chaîne 'toto' n'a pas été trouvée dans la réponse."
                    fi'''
                    def code_retour = sh(script: 'curl -i -H "accept: application/json" https://www.devops-youss.cloudns.ph/users/1 | grep -i "200"', returnStatus: true) 
                    // def count_return = sh '''curl 'GET' -H 'accept: application/json' https://www.devops-youss.cloudns.ph/users/1 ''' 
                    def count_return = sh(script: "curl 'GET' -H 'accept: application/json' https://www.devops-youss.cloudns.ph/users/1", returnStdout: true).trim()
                    

                    if (code_retour == 200 ) {
                        echo $count_return
                    } else {
                        error("pas de retour de l'api")
                    }    
                }
            }
        }

        stage('Production deployment') {
            steps {
                // Create an Approval Button with a timeout of 15minutes.
                // this require a manuel validation in order to deploy on production environment
                timeout(time: 15, unit: "MINUTES") {
                    input message: 'Do you want to deploy in production ?', ok: 'Yes'
                }
                script {
                    sh '''
                    sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" myapp1/values.yaml     
                    helm upgrade --install myapp-release-prod myapp1/ --values myapp1/values.yaml -f myapp1/values-prod.yaml -n prod --create-namespace
                    '''
                }
            }
        }

        stage('Prune Docker data') {
                steps {
                    sh 'docker system prune -a --volumes -f'
                }

        }
    }
    
    post { // send email when the job has failed
        success {
            script {
                slackSend botUser: true, color: 'good', message: "Successful :jenkins-${JOB_NAME}-${BUILD_ID}", teamDomain: 'DEVOPS TEAM', tokenCredentialId: 'slack-bot-token'
            }
        }
        
        failure {
            script {
                slackSend botUser: true, color: 'danger', message: "Failure :jenkins-${JOB_NAME}-${BUILD_ID}", teamDomain: 'DEVOPS TEAM', tokenCredentialId: 'slack-bot-token'
            }
        }
        // ..
        /*
        failure {
            echo "This will run if the job failed"
            mail to: "youssef.kadi@gmail.com",
                subject: "${env.JOB_NAME} - Build # ${env.BUILD_ID} has failed",
                body: "For more info on the pipeline failure, check out the console output at ${env.BUILD_URL}"
        }
        */
        // ..
    }
}

