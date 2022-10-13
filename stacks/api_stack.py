import aws_cdk
from aws_cdk import (
    Stack, Expiration, Duration, CfnOutput,
    aws_cognito as cognito,
    aws_appsync as appsync,
    aws_dynamodb as ddb,
    aws_lambda as _lambda,
    aws_appsync_alpha as appsynch_alpha
)
from constructs import Construct

class AwsAppSyncApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.userPool = cognito.UserPool(self, 'products-user-pool',
                                         self_sign_up_enabled=True,
                                         account_recovery=cognito.AccountRecovery.PHONE_AND_EMAIL,
                                         user_verification=cognito.UserVerificationConfig(
                                             email_style=cognito.VerificationEmailStyle.CODE
                                         ),
                                         auto_verify=cognito.AutoVerifiedAttrs(
                                             email=True
                                         ),
                                         standard_attributes=cognito.StandardAttributes(
                                             email=cognito.StandardAttribute(
                                                 required=True,
                                                 mutable=True
                                             )
                                         ))
        self.userPoolClient = cognito.UserPoolClient
        
        self.api = appsynch_alpha.GraphqlApi(self, 'products_app',
                                             name='products-api',
                                             log_config= appsynch_alpha.LogConfig(
                                                 field_log_level= appsynch_alpha.FieldLogLevel.ALL,
                                             ),
                                             schema= appsynch_alpha.Schema.from_asset('./graphql/schema.graphql'),
                                             authorization_config= appsynch_alpha.AuthorizationConfig(
                                                 default_authorization=appsynch_alpha.AuthorizationMode(
                                                     authorization_type=appsynch_alpha.AuthorizationType.API_KEY,
                                                     api_key_config= Expiration.after(Duration.days(30))
                                                 ),
                                                 additional_authorization_modes=[appsynch_alpha.AuthorizationMode(
                                                     authorization_type=appsynch_alpha.AuthorizationType.USER_POOL,
                                                     user_pool_config=appsynch_alpha.UserPoolConfig(
                                                         user_pool= self.userPool
                                                     )
                                                 )]
                                             ))
        
        self.productLambda = _lambda.Function(self, 'AppSyncProductHandler',
                                              runtime= _lambda.Runtime.NODEJS_12_X,
                                              handler= 'main.handler',
                                              code= _lambda.Code.from_asset('lambda-fns'),
                                              memory_size= 1024)
        
        self.lambdaDataSource = self.api.add_lambda_data_source('lambdaDatasource', self.productLambda)
        
        self.lambdaDataSource.create_resolver(
                                              type_name= 'Query',
                                              field_name= 'getProductById'
        )
        
        self.lambdaDataSource.create_resolver(
                                              type_name= 'Query',
                                              field_name= 'listProducts'
        )
        
        self.lambdaDataSource.create_resolver(
                                              type_name= 'Query',
                                              field_name= 'productsByCategory'
        )
        
        self.lambdaDataSource.create_resolver(
                                              type_name= 'Mutation',
                                              field_name= 'createProduct'
        )
        
        self.lambdaDataSource.create_resolver(
                                              type_name= 'Mutation',
                                              field_name= 'deleteProduct'
        )
        
        self.lambdaDataSource.create_resolver(
                                              type_name= 'Mutation',
                                              field_name= 'updateProduct'
        )
        
        self.productTable = ddb.Table(self, 'CDKProductTable',
                                 billing_mode= ddb.BillingMode.PAY_PER_REQUEST,
                                 partition_key= ddb.Attribute(
                                     name='id',
                                     type= ddb.AttributeType.STRING
                                 ))
        # when you query by category, you're quierying by using this global secondary index
        self.productTable.add_global_secondary_index(
            index_name= 'productsByCategory',
            partition_key= ddb.Attribute(
                name= 'category',
                type= ddb.AttributeType.STRING,
            ))
        
        self.productTable.grant_full_access(self.productLambda)
        
        self.productLambda.add_environment('PRODUCT_TABLE', self.productTable.table_name)
        
        this = CfnOutput(self, 'GraphQLAPIURL',
                         value= self.api.graphql_url)
        
        this = CfnOutput(self, 'AppSynchAPIKey',
                         value= self.api.api_key or '')
        
        this = CfnOutput(self, 'ProjectRegion',
                         value= self.region)
        
        this = CfnOutput(self, 'UserPoolId',
                         value= self.userPool.user_pool_id)
        
        this = CfnOutput(self, 'UserPoolClientId',
                         value= self.userPoolClient.user_pool_client_id)
        
        this = CfnOutput(self, 'GraphQLAPIURL',
                         value= self.api.graphql_url)