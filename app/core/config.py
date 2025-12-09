"""
Application configuration using Pydantic v2 settings.
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(alias="APP_NAME")
    environment: str = Field(alias="ENVIRONMENT")
    debug: bool = Field(alias="DEBUG")

    # Database
    database_url: str = Field(alias="DATABASE_URL")
    database_url_sync: str = Field(alias="DATABASE_URL_SYNC")

    # Security
    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(alias="ALGORITHM")
    access_token_expire_minutes: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # AI Services (Free)
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")

    # Email Configuration - MailerSend
    mailersend_api_key: Optional[str] = Field(default=None, alias="MAILERSEND_API_KEY")
    mailersend_sender_email: str = Field(alias="MAILERSEND_SENDER_EMAIL")
    mailersend_sender_name: str = Field(alias="MAILERSEND_SENDER_NAME")
    from_email: str = Field(alias="FROM_EMAIL")
    email_verification_enabled: bool = Field(alias="EMAIL_VERIFICATION_ENABLED")

    # File Storage
    cloudinary_cloud_name: Optional[str] = Field(default=None, alias="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: Optional[str] = Field(default=None, alias="CLOUDINARY_API_KEY")
    cloudinary_api_secret: Optional[str] = Field(default=None, alias="CLOUDINARY_API_SECRET")

    # Redis
    redis_url: str = Field(alias="REDIS_URL")

    # SMS - Termii
    termii_api_key: Optional[str] = Field(default=None, alias="TERMII_API_KEY")
    termii_sender_id: str = Field(alias="TERMII_SENDER_ID")
    termii_base_url: str = Field(alias="TERMII_BASE_URL")

    # Video / Educational APIs (Free)
    youtube_api_key: Optional[str] = Field(default=None, alias="YOUTUBE_API_KEY")

    # Educational Content API URLs
    coursera_api_url: str = Field(alias="COURSERA_API_URL")
    edx_api_url: str = Field(alias="EDX_API_URL")
    futurelearn_api_url: str = Field(alias="FUTURELEARN_API_URL")
    khan_academy_api_url: str = Field(alias="KHAN_ACADEMY_API_URL")
    youtube_search_api_url: str = Field(alias="YOUTUBE_SEARCH_API_URL")
    mit_ocw_api_url: str = Field(alias="MIT_OCW_API_URL")

    # Educational Provider Websites
    coursera_website_url: str = Field(alias="COURSERA_WEBSITE_URL")
    edx_website_url: str = Field(alias="EDX_WEBSITE_URL")
    futurelearn_website_url: str = Field(alias="FUTURELEARN_WEBSITE_URL")
    khan_academy_website_url: str = Field(alias="KHAN_ACADEMY_WEBSITE_URL")
    youtube_education_url: str = Field(alias="YOUTUBE_EDUCATION_URL")
    mit_ocw_website_url: str = Field(alias="MIT_OCW_WEBSITE_URL")

    # Job Search API URLs
    remoteok_api_url: str = Field(alias="REMOTEOK_API_URL")
    remotive_api_url: str = Field(alias="REMOTIVE_API_URL")
    github_api_url: str = Field(alias="GITHUB_API_URL")
    angellist_api_url: str = Field(alias="ANGELLIST_API_URL")
    linkedin_rapidapi_url: str = Field(alias="LINKEDIN_RAPIDAPI_URL")
    indeed_rapidapi_url: str = Field(alias="INDEED_RAPIDAPI_URL")
    crunchbase_api_url: str = Field(alias="CRUNCHBASE_API_URL")

    # Job Search API Keys (Optional)
    linkedin_rapidapi_key: Optional[str] = Field(default=None, alias="LINKEDIN_RAPIDAPI_KEY")
    indeed_rapidapi_key: Optional[str] = Field(default=None, alias="INDEED_RAPIDAPI_KEY")
    crunchbase_api_key: Optional[str] = Field(default=None, alias="CRUNCHBASE_API_KEY")

    # Case Study URLs (Project Simulations)
    netflix_tech_blog_url: str = Field(alias="NETFLIX_TECH_BLOG_URL")
    spotify_engineering_url: str = Field(alias="SPOTIFY_ENGINEERING_URL")
    who_covax_url: str = Field(alias="WHO_COVAX_URL")
    tesla_gigafactory_url: str = Field(alias="TESLA_GIGAFACTORY_URL")
    azure_cognitive_services_url: str = Field(alias="AZURE_COGNITIVE_SERVICES_URL")
    emirates_digital_innovation_url: str = Field(alias="EMIRATES_DIGITAL_INNOVATION_URL")
    worldbank_financial_inclusion_url: str = Field(alias="WORLDBANK_FINANCIAL_INCLUSION_URL")
    amazon_prime_press_url: str = Field(alias="AMAZON_PRIME_PRESS_URL")

    # Job Scraping
    job_scraping_enabled: bool = Field(alias="JOB_SCRAPING_ENABLED")

    # CORS
    allowed_hosts: str = Field(alias="ALLOWED_HOSTS")

    # Platform URLs
    frontend_url: str = Field(alias="FRONTEND_URL")
    platform_url: str = Field(alias="PLATFORM_URL")
    help_center_url: str = Field(alias="HELP_CENTER_URL")

    # Social Media
    social_linkedin: str = Field(alias="SOCIAL_LINKEDIN")
    social_twitter: str = Field(alias="SOCIAL_TWITTER")
    social_facebook: str = Field(alias="SOCIAL_FACEBOOK")
    social_instagram: str = Field(alias="SOCIAL_INSTAGRAM")

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ("development", "dev", "local")

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")


settings = Settings()