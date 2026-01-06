"""Main CDK Stack for Habit Tracker RPG."""
from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_cognito as cognito,
    aws_iam as iam,
)


class HabitTrackerRpgStack(Stack):
    """Main stack for Habit Tracker RPG infrastructure."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str = "dev",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.env_name = env_name
        self.prefix = f"habit-tracker-rpg-{env_name}"

        # Create DynamoDB tables
        self.tables = self._create_dynamodb_tables()

        # Create Cognito User Pool
        self.user_pool, self.user_pool_client = self._create_cognito()

        # Create Lambda layer for dependencies
        self.lambda_layer = self._create_lambda_layer()

        # Create Lambda functions
        self.lambda_functions = self._create_lambda_functions()

        # Create API Gateway
        self.api = self._create_api_gateway()

        # Output values
        self._create_outputs()

    def _create_dynamodb_tables(self) -> dict:
        """Create DynamoDB tables."""
        tables = {}

        # Users table
        tables["users"] = dynamodb.Table(
            self,
            "UsersTable",
            table_name=f"{self.prefix}-users",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY if self.env_name == "dev" else RemovalPolicy.RETAIN,
        )

        # Habits table
        tables["habits"] = dynamodb.Table(
            self,
            "HabitsTable",
            table_name=f"{self.prefix}-habits",
            partition_key=dynamodb.Attribute(
                name="habit_id",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY if self.env_name == "dev" else RemovalPolicy.RETAIN,
        )

        # Add GSI for querying habits by user
        tables["habits"].add_global_secondary_index(
            index_name="user_id-index",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING,
            ),
        )

        # Records table
        tables["records"] = dynamodb.Table(
            self,
            "RecordsTable",
            table_name=f"{self.prefix}-records",
            partition_key=dynamodb.Attribute(
                name="habit_id",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="record_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY if self.env_name == "dev" else RemovalPolicy.RETAIN,
        )

        # Add GSI for querying records by user
        tables["records"].add_global_secondary_index(
            index_name="user_id-index",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="completed_date",
                type=dynamodb.AttributeType.STRING,
            ),
        )

        # User Achievements table
        tables["user_achievements"] = dynamodb.Table(
            self,
            "UserAchievementsTable",
            table_name=f"{self.prefix}-user-achievements",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="achievement_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY if self.env_name == "dev" else RemovalPolicy.RETAIN,
        )

        # User Jobs table
        tables["user_jobs"] = dynamodb.Table(
            self,
            "UserJobsTable",
            table_name=f"{self.prefix}-user-jobs",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="job_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY if self.env_name == "dev" else RemovalPolicy.RETAIN,
        )

        return tables

    def _create_cognito(self):
        """Create Cognito User Pool."""
        user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=f"{self.prefix}-users",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True),
            ),
            custom_attributes={
                "display_name": cognito.StringAttribute(mutable=True),
                "timezone": cognito.StringAttribute(mutable=True),
            },
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.DESTROY if self.env_name == "dev" else RemovalPolicy.RETAIN,
        )

        user_pool_client = user_pool.add_client(
            "UserPoolClient",
            user_pool_client_name=f"{self.prefix}-client",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
            generate_secret=False,
            access_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
        )

        return user_pool, user_pool_client

    def _create_lambda_layer(self):
        """Create Lambda layer for Python dependencies."""
        return lambda_.LayerVersion(
            self,
            "DependenciesLayer",
            layer_version_name=f"{self.prefix}-dependencies",
            code=lambda_.Code.from_asset("../layers/dependencies"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="Dependencies for Habit Tracker RPG Lambda functions",
        )

    def _create_lambda_functions(self) -> dict:
        """Create Lambda functions."""
        functions = {}

        # Common environment variables
        common_env = {
            "USERS_TABLE": self.tables["users"].table_name,
            "HABITS_TABLE": self.tables["habits"].table_name,
            "RECORDS_TABLE": self.tables["records"].table_name,
            "USER_ACHIEVEMENTS_TABLE": self.tables["user_achievements"].table_name,
            "USER_JOBS_TABLE": self.tables["user_jobs"].table_name,
            "COGNITO_USER_POOL_ID": self.user_pool.user_pool_id,
            "COGNITO_CLIENT_ID": self.user_pool_client.user_pool_client_id,
            "COGNITO_REGION": self.region,
        }

        # Lambda execution role
        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )

        # Add DynamoDB permissions
        for table in self.tables.values():
            table.grant_read_write_data(lambda_role)

        # Add Cognito permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "cognito-idp:AdminConfirmSignUp",
                    "cognito-idp:AdminGetUser",
                ],
                resources=[self.user_pool.user_pool_arn],
            )
        )

        # Handler mapping
        handlers = {
            # Auth
            "auth_signup": "src.handlers.auth.sign_up",
            "auth_signin": "src.handlers.auth.sign_in",
            "auth_signout": "src.handlers.auth.sign_out",
            "auth_refresh": "src.handlers.auth.refresh_token",
            "auth_change_password": "src.handlers.auth.change_password",
            # Users
            "users_get_profile": "src.handlers.users.get_my_profile",
            "users_update_profile": "src.handlers.users.update_my_profile",
            "users_get_stats": "src.handlers.users.get_my_stats",
            # Habits
            "habits_list": "src.handlers.habits.list_habits",
            "habits_create": "src.handlers.habits.create_habit",
            "habits_get": "src.handlers.habits.get_habit",
            "habits_update": "src.handlers.habits.update_habit",
            "habits_delete": "src.handlers.habits.delete_habit",
            "habits_archive": "src.handlers.habits.archive_habit",
            # Records
            "records_list": "src.handlers.records.list_habit_records",
            "records_create": "src.handlers.records.create_habit_record",
            "records_update": "src.handlers.records.update_habit_record",
            "records_delete": "src.handlers.records.delete_habit_record",
            "records_today": "src.handlers.records.get_today_records",
            # Stats
            "stats_daily": "src.handlers.stats.get_daily_stats",
            "stats_weekly": "src.handlers.stats.get_weekly_stats",
            "stats_monthly": "src.handlers.stats.get_monthly_stats",
            # Achievements
            "achievements_list": "src.handlers.achievements.list_achievements",
            "achievements_get": "src.handlers.achievements.get_achievement",
            # Jobs
            "jobs_list": "src.handlers.jobs.list_jobs",
            "jobs_get": "src.handlers.jobs.get_job",
            "jobs_equip": "src.handlers.jobs.equip_job",
        }

        for name, handler in handlers.items():
            functions[name] = lambda_.Function(
                self,
                f"Lambda-{name}",
                function_name=f"{self.prefix}-{name}",
                runtime=lambda_.Runtime.PYTHON_3_11,
                handler=handler,
                code=lambda_.Code.from_asset("../"),
                role=lambda_role,
                environment=common_env,
                layers=[self.lambda_layer],
                timeout=Duration.seconds(30),
                memory_size=256,
            )

        return functions

    def _create_api_gateway(self):
        """Create API Gateway."""
        api = apigw.RestApi(
            self,
            "Api",
            rest_api_name=f"{self.prefix}-api",
            description="Habit Tracker RPG API",
            deploy_options=apigw.StageOptions(
                stage_name=self.env_name,
                logging_level=apigw.MethodLoggingLevel.INFO,
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        # Cognito authorizer
        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[self.user_pool],
        )

        # Helper function to create integration
        def create_integration(function_name: str) -> apigw.LambdaIntegration:
            return apigw.LambdaIntegration(
                self.lambda_functions[function_name],
                proxy=True,
            )

        # Auth endpoints (no auth required)
        auth = api.root.add_resource("auth")
        auth.add_resource("signup").add_method("POST", create_integration("auth_signup"))
        auth.add_resource("signin").add_method("POST", create_integration("auth_signin"))
        auth.add_resource("signout").add_method(
            "POST",
            create_integration("auth_signout"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        auth.add_resource("refresh").add_method("POST", create_integration("auth_refresh"))
        auth.add_resource("password").add_resource("change").add_method(
            "POST",
            create_integration("auth_change_password"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # Users endpoints
        users = api.root.add_resource("users")
        me = users.add_resource("me")
        me.add_method(
            "GET",
            create_integration("users_get_profile"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        me.add_method(
            "PUT",
            create_integration("users_update_profile"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        me.add_resource("stats").add_method(
            "GET",
            create_integration("users_get_stats"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # Habits endpoints
        habits = api.root.add_resource("habits")
        habits.add_method(
            "GET",
            create_integration("habits_list"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        habits.add_method(
            "POST",
            create_integration("habits_create"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        habit_id = habits.add_resource("{habitId}")
        habit_id.add_method(
            "GET",
            create_integration("habits_get"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        habit_id.add_method(
            "PUT",
            create_integration("habits_update"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        habit_id.add_method(
            "DELETE",
            create_integration("habits_delete"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        habit_id.add_resource("archive").add_method(
            "POST",
            create_integration("habits_archive"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # Records endpoints
        records = habit_id.add_resource("records")
        records.add_method(
            "GET",
            create_integration("records_list"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        records.add_method(
            "POST",
            create_integration("records_create"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        record_id = records.add_resource("{recordId}")
        record_id.add_method(
            "PUT",
            create_integration("records_update"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        record_id.add_method(
            "DELETE",
            create_integration("records_delete"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # Today's records
        api.root.add_resource("records").add_resource("today").add_method(
            "GET",
            create_integration("records_today"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # Stats endpoints
        stats = api.root.add_resource("stats")
        stats.add_resource("daily").add_method(
            "GET",
            create_integration("stats_daily"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        stats.add_resource("weekly").add_method(
            "GET",
            create_integration("stats_weekly"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        stats.add_resource("monthly").add_method(
            "GET",
            create_integration("stats_monthly"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # Achievements endpoints
        achievements = api.root.add_resource("achievements")
        achievements.add_method(
            "GET",
            create_integration("achievements_list"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        achievements.add_resource("{achievementId}").add_method(
            "GET",
            create_integration("achievements_get"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        # Jobs endpoints
        jobs = api.root.add_resource("jobs")
        jobs.add_method(
            "GET",
            create_integration("jobs_list"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        job_id = jobs.add_resource("{jobId}")
        job_id.add_method(
            "GET",
            create_integration("jobs_get"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )
        job_id.add_resource("equip").add_method(
            "POST",
            create_integration("jobs_equip"),
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO,
        )

        return api

    def _create_outputs(self):
        """Create CloudFormation outputs."""
        CfnOutput(
            self,
            "ApiUrl",
            value=self.api.url,
            description="API Gateway URL",
        )

        CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID",
        )

        CfnOutput(
            self,
            "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID",
        )
