"""
User-related database models using SQLAlchemy 2.0+.
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base
from app.core.utils import utc_now

if TYPE_CHECKING:
    from app.database.platform_models import ProjectSimulation, CV, JobApplication, Portfolio, UserAchievement
    from app.database.community_models import ForumPost, ForumComment, Mentorship  
    from app.database.job_models import SavedJob, JobAlert
    from app.database.cv_models import CVExport
    from app.database.gamification_models import UserLevel


class UserRole(str, enum.Enum):
    """User role enumeration for RBAC."""
    USER = "user"              # Regular job seeker/learner
    RECRUITER = "recruiter"    # Recruiter who can post jobs
    COMPANY = "company"        # Company representative
    MENTOR = "mentor"          # Mentor who provides guidance
    ADMIN = "admin"            # Platform administrator


class SkillLevel(int, enum.Enum):
    """Skill level enumeration."""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


class User(Base):
    """User model for authentication and basic info."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False, index=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    mentor_profile: Mapped[Optional["MentorProfile"]] = relationship("MentorProfile", back_populates="user", uselist=False)
    projects: Mapped[List["ProjectSimulation"]] = relationship("ProjectSimulation", back_populates="user")
    cvs: Mapped[List["CV"]] = relationship("CV", back_populates="user")
    cv_exports: Mapped[List["CVExport"]] = relationship("CVExport", back_populates="user")
    job_applications: Mapped[List["JobApplication"]] = relationship("JobApplication", back_populates="user")
    job_alerts: Mapped[List["JobAlert"]] = relationship("JobAlert", back_populates="user")
    saved_jobs: Mapped[List["SavedJob"]] = relationship("SavedJob", back_populates="user")
    portfolios: Mapped[List["Portfolio"]] = relationship("Portfolio", back_populates="user")
    forum_posts: Mapped[List["ForumPost"]] = relationship("ForumPost", back_populates="author")
    forum_comments: Mapped[List["ForumComment"]] = relationship("ForumComment", back_populates="author")
    mentorships_as_mentee: Mapped[List["Mentorship"]] = relationship("Mentorship", foreign_keys="Mentorship.mentee_id", back_populates="mentee")
    mentorships_as_mentor: Mapped[List["Mentorship"]] = relationship("Mentorship", foreign_keys="Mentorship.mentor_id", back_populates="mentor")
    achievements: Mapped[List["UserAchievement"]] = relationship("UserAchievement", back_populates="user")
    level_progression: Mapped[Optional["UserLevel"]] = relationship("UserLevel", back_populates="user", uselist=False)

# NEW — Payments / Subscriptions
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )


    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_user_active_role', 'is_active', 'role'),
        Index('idx_user_verified_active', 'is_verified', 'is_active'),
        Index('idx_user_created_role', 'created_at', 'role'),
        Index('idx_user_last_login_active', 'last_login', 'is_active'),
    )


class Profile(Base):
    """User profile with detailed information."""
    
    __tablename__ = "profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Personal information
    first_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Professional information
    current_job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    company: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # Career goals
    career_goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_industries: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    preferred_work_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)  # remote, onsite, hybrid
    
    # Learning preferences
    learning_style: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)  # visual, auditory, kinesthetic
    preferred_methodologies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    
    # Job Search and Auto-Application Preferences
    job_alerts_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    auto_apply_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    auto_apply_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON with criteria settings
    max_daily_auto_applications: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    min_match_score_threshold: Mapped[float] = mapped_column(default=0.75, nullable=False)
    preferred_job_types: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of job types
    salary_expectations_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)  # in thousands
    salary_expectations_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)  # in thousands
    excluded_companies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of company names to avoid
    auto_apply_only_remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    require_manual_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Contact information
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Location
    country: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    city: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    # UI Preferences (language, theme, notifications, privacy)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Profile completion
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False, index=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    skills: Mapped[List["UserSkill"]] = relationship("UserSkill", back_populates="profile", cascade="all, delete-orphan")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_profile_location', 'country', 'city'),
        Index('idx_profile_experience_title', 'years_of_experience', 'current_job_title'),
        Index('idx_profile_completion_mode', 'is_complete', 'preferred_work_mode'),
        Index('idx_profile_company_experience', 'company', 'years_of_experience'),
        Index('idx_profile_auto_apply', 'auto_apply_enabled', 'job_alerts_enabled'),
        Index('idx_profile_salary_auto', 'salary_expectations_min', 'auto_apply_enabled'),
        Index('idx_profile_remote_auto', 'auto_apply_only_remote', 'auto_apply_enabled'),
        Index('idx_profile_approval_auto', 'require_manual_approval', 'auto_apply_enabled'),
    )


class UserSkill(Base):
    """User skills with proficiency levels."""
    
    __tablename__ = "user_skills"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    skill_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    skill_category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # technical, soft, methodology
    proficiency_level: Mapped[SkillLevel] = mapped_column(SQLEnum(SkillLevel), default=SkillLevel.BEGINNER, nullable=False, index=True)
    
    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    verified_by_project: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="skills")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_skill_profile_category', 'profile_id', 'skill_category'),
        Index('idx_skill_name_level', 'skill_name', 'proficiency_level'),
        Index('idx_skill_category_verified', 'skill_category', 'is_verified'),
        Index('idx_skill_profile_verified', 'profile_id', 'is_verified'),
    )


class MentorProfile(Base):
    """Mentor-specific profile information."""
    
    __tablename__ = "mentor_profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Mentor qualifications
    certifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    specializations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    mentoring_experience_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Availability
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    max_mentees: Mapped[int] = mapped_column(Integer, default=5, nullable=False, index=True)
    current_mentees_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    
    # Rates and preferences
    hourly_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)  # in cents
    preferred_communication: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # video, text, both
    available_time_slots: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON as string
    
    # Mentor bio
    mentor_bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approach_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Rating and reviews
    average_rating: Mapped[Optional[float]] = mapped_column(nullable=True, index=True)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    
    # Status
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="mentor_profile")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_mentor_available_approved', 'is_available', 'is_approved'),
        Index('idx_mentor_rating_reviews', 'average_rating', 'total_reviews'),
        Index('idx_mentor_rate_available', 'hourly_rate', 'is_available'),
        Index('idx_mentor_capacity', 'current_mentees_count', 'max_mentees'),
    )