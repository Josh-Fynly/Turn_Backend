"""
API endpoints for Project Simulations - Virtual PM projects and skill assessments.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.database.user_models import User
from app.database.project_models import ProjectSimulation
from app.database.platform_models import SimulationStatus
from app.schemas.project_schemas import (
    ProjectSimulationResponse, CreateSimulationRequest,
    UpdateSimulationRequest, SimulationStatsResponse
)

from app.services.simulation_engine import (
    load_simulation,
    apply_action,
    generate_score,
    generate_coach_summary,
)


router = APIRouter(prefix="/api/v1/simulations", tags=["Project Simulations"])


@router.get("/templates", response_model=List[dict])
async def get_simulation_templates():
    """Get real project simulation templates based on industry case studies."""
    # These are based on real project management scenarios and case studies
    templates = [
        {
            "id": 1,
            "title": "Netflix Streaming Platform Scale-Up",
            "description": "Lead the infrastructure scaling project that enabled Netflix to handle 200M+ concurrent users during peak times. Based on Netflix's actual 2019-2020 scaling challenges.",
            "industry": "Technology/Media",
            "complexity_level": 5,
            "duration_weeks": 16,
            "team_size": 12,
            "budget": 800,
            "skills_focus": ["Cloud Architecture", "Performance Optimization", "Cross-functional Leadership"],
            "real_world_basis": "Netflix 2020 Pandemic Traffic Surge",
            "learning_outcomes": ["Managing 300% traffic increase", "Multi-region deployment", "Crisis management"],
            "case_study_url": settings.netflix_tech_blog_url,
            "industry_partner": "Netflix (Case Study)"
        },
        {
            "id": 2,
            "title": "Spotify's Agile Transformation at Scale",
            "description": "Implement the Spotify Model across a 2000-person engineering organization. Transform from traditional waterfall to autonomous squads and tribes.",
            "industry": "Technology/Music",
            "complexity_level": 4,
            "duration_weeks": 24,
            "team_size": 15,
            "budget": 500,
            "skills_focus": ["Agile Transformation", "Organizational Change", "Scaled Agile"],
            "real_world_basis": "Spotify's Engineering Culture Evolution",
            "learning_outcomes": ["Autonomous team structure", "Scaling agile practices", "Cultural transformation"],
            "case_study_url": settings.spotify_engineering_url,
            "industry_partner": "Spotify (Case Study)"
        },
        {
            "id": 3,
            "title": "WHO COVID-19 Vaccine Distribution Project",
            "description": "Coordinate global vaccine distribution logistics involving 195 countries, cold chain management, and real-time tracking systems.",
            "industry": "Healthcare/Pharmaceuticals",
            "complexity_level": 5,
            "duration_weeks": 20,
            "team_size": 25,
            "budget": 1200,
            "skills_focus": ["Global Program Management", "Supply Chain", "Crisis Response"],
            "real_world_basis": "COVAX Global Vaccine Distribution 2021",
            "learning_outcomes": ["Multi-stakeholder coordination", "Logistics optimization", "Global crisis management"],
            "case_study_url": settings.who_covax_url,
            "industry_partner": "World Health Organization (Case Study)"
        },
        {
            "id": 4,
            "title": "Tesla Gigafactory Berlin Production Ramp",
            "description": "Launch Tesla's European Gigafactory from groundbreaking to full production capacity of 500,000 vehicles annually.",
            "industry": "Automotive/Manufacturing",
            "complexity_level": 4,
            "duration_weeks": 28,
            "team_size": 20,
            "budget": 2000,
            "skills_focus": ["Manufacturing Operations", "International Expansion", "Regulatory Compliance"],
            "real_world_basis": "Tesla Gigafactory Berlin 2019-2022",
            "learning_outcomes": ["International project delivery", "Regulatory navigation", "Production scaling"],
            "case_study_url": settings.tesla_gigafactory_url,
            "industry_partner": "Tesla (Case Study)"
        },
        {
            "id": 5,
            "title": "Microsoft Azure AI Platform Launch",
            "description": "Lead the development and launch of Azure's enterprise AI platform, including machine learning services and cognitive APIs.",
            "industry": "Technology/Cloud Services",
            "complexity_level": 4,
            "duration_weeks": 18,
            "team_size": 18,
            "budget": 600,
            "skills_focus": ["Product Management", "AI/ML Strategy", "Enterprise Sales"],
            "real_world_basis": "Microsoft Azure Cognitive Services Launch",
            "learning_outcomes": ["Product-market fit", "Technical complexity management", "Go-to-market strategy"],
            "case_study_url": settings.azure_cognitive_services_url,
            "industry_partner": "Microsoft (Case Study)"
        },
        {
            "id": 6,
            "title": "Emirates Airline Digital Transformation",
            "description": "Transform Emirates' customer experience through digital innovation: mobile check-in, IoT baggage tracking, and AI customer service.",
            "industry": "Aviation/Travel",
            "complexity_level": 3,
            "duration_weeks": 14,
            "team_size": 12,
            "budget": 400,
            "skills_focus": ["Digital Transformation", "Customer Experience", "Legacy System Integration"],
            "real_world_basis": "Emirates Digital Innovation Initiative 2020-2021",
            "learning_outcomes": ["Customer journey optimization", "Legacy system modernization", "Service design"],
            "case_study_url": settings.emirates_digital_innovation_url,
            "industry_partner": "Emirates (Case Study)"
        },
        {
            "id": 7,
            "title": "World Bank Financial Inclusion Project",
            "description": "Deploy mobile banking infrastructure across 15 African countries to provide financial services to 50 million unbanked individuals.",
            "industry": "Financial Services/Development",
            "complexity_level": 5,
            "duration_weeks": 32,
            "team_size": 30,
            "budget": 1500,
            "skills_focus": ["International Development", "Financial Technology", "Multi-country Coordination"],
            "real_world_basis": "World Bank Financial Inclusion Support Framework",
            "learning_outcomes": ["Cross-cultural management", "Impact measurement", "Sustainable development"],
            "case_study_url": settings.worldbank_financial_inclusion_url,
            "industry_partner": "World Bank (Case Study)"
        },
        {
            "id": 8,
            "title": "Amazon Prime Video Global Content Strategy",
            "description": "Launch Amazon Prime Video's local content production strategy across 25 international markets with culturally relevant programming.",
            "industry": "Entertainment/Streaming",
            "complexity_level": 3,
            "duration_weeks": 20,
            "team_size": 16,
            "budget": 700,
            "skills_focus": ["Content Strategy", "International Markets", "Cultural Adaptation"],
            "real_world_basis": "Amazon Prime Video International Expansion 2020-2022",
            "learning_outcomes": ["Market localization", "Content portfolio management", "Global brand consistency"],
            "case_study_url": settings.amazon_prime_press_url,
            "industry_partner": "Amazon (Case Study)"
        }
    ]
    return templates


@router.post("/start", response_model=ProjectSimulationResponse)
async def start_simulation(
    request: CreateSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new project simulation."""
    simulation = ProjectSimulation(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        industry=request.industry,
        complexity_level=request.complexity_level,
        team_size=request.team_size,
        duration_weeks=request.duration_weeks,
        budget=request.budget,
        status=SimulationStatus.NOT_STARTED,
        current_phase="Initiation",
        completion_percentage=0
    )
    
    db.add(simulation)
    await db.commit()
    await db.refresh(simulation)
    
    return ProjectSimulationResponse.model_validate(simulation)


@router.get("/", response_model=List[ProjectSimulationResponse])
async def get_user_simulations(
    status: Optional[SimulationStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's project simulations."""
    query = select(ProjectSimulation).where(
        ProjectSimulation.user_id == current_user.id
    )
    
    if status:
        query = query.where(ProjectSimulation.status == status)
    
    query = query.order_by(desc(ProjectSimulation.created_at))
    
    result = await db.execute(query)
    simulations = result.scalars().all()
    
    return [ProjectSimulationResponse.model_validate(sim) for sim in simulations]


@router.get("/{simulation_id}", response_model=ProjectSimulationResponse)
async def get_simulation(
    simulation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project simulation."""
    result = await db.execute(
        select(ProjectSimulation)
        .where(and_(
            ProjectSimulation.id == simulation_id,
            ProjectSimulation.user_id == current_user.id
        ))
    )
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    return ProjectSimulationResponse.model_validate(simulation)


@router.put("/{simulation_id}", response_model=ProjectSimulationResponse)
async def update_simulation(
    simulation_id: int,
    request: UpdateSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update project simulation progress."""
    result = await db.execute(
        select(ProjectSimulation)
        .where(and_(
            ProjectSimulation.id == simulation_id,
            ProjectSimulation.user_id == current_user.id
        ))
    )
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Update fields
    if request.status is not None:
        simulation.status = request.status
        
        # Update timestamps based on status
        if request.status == SimulationStatus.IN_PROGRESS and not simulation.started_at:
            simulation.started_at = datetime.utcnow()
        elif request.status == SimulationStatus.COMPLETED:
            simulation.completed_at = datetime.utcnow()
            simulation.completion_percentage = 100
    
    if request.current_phase is not None:
        simulation.current_phase = request.current_phase
    
    if request.completion_percentage is not None:
        if not 0 <= request.completion_percentage <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completion percentage must be between 0 and 100"
            )
        simulation.completion_percentage = request.completion_percentage
    
    if request.skill_assessments is not None:
        simulation.skill_assessments = request.skill_assessments
    
    if request.artifacts_created is not None:
        simulation.artifacts_created = request.artifacts_created
    
    simulation.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(simulation)
    
    return ProjectSimulationResponse.model_validate(simulation)


@router.post("/{simulation_id}/complete", response_model=ProjectSimulationResponse)
async def complete_simulation(
    simulation_id: int,
    final_score: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete a project simulation."""
    result = await db.execute(
        select(ProjectSimulation)
        .where(and_(
            ProjectSimulation.id == simulation_id,
            ProjectSimulation.user_id == current_user.id
        ))
    )
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    if simulation.status == SimulationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation is already completed"
        )
    
    # Mark as completed
    simulation.status = SimulationStatus.COMPLETED
    simulation.completed_at = datetime.utcnow()
    simulation.completion_percentage = 100
    
    if final_score is not None:
        if not 0 <= final_score <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Final score must be between 0 and 100"
            )
        simulation.final_score = final_score
    
    await db.commit()
    await db.refresh(simulation)
    
    return ProjectSimulationResponse.model_validate(simulation)


@router.get("/{simulation_id}/artifacts", response_model=dict)
async def get_simulation_artifacts(
    simulation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get artifacts created during simulation."""
    result = await db.execute(
        select(ProjectSimulation)
        .where(and_(
            ProjectSimulation.id == simulation_id,
            ProjectSimulation.user_id == current_user.id
        ))
    )
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Mock artifacts data - in production this would be stored in the database
    artifacts = {
        "project_charter": {
            "title": "Project Charter - E-commerce Platform",
            "completed": True,
            "download_url": f"/api/v1/simulations/{simulation_id}/artifacts/charter.pdf"
        },
        "risk_register": {
            "title": "Risk Management Register",
            "completed": True,
            "download_url": f"/api/v1/simulations/{simulation_id}/artifacts/risk-register.xlsx"
        },
        "stakeholder_matrix": {
            "title": "Stakeholder Analysis Matrix",
            "completed": True,
            "download_url": f"/api/v1/simulations/{simulation_id}/artifacts/stakeholder-matrix.pdf"
        },
        "project_schedule": {
            "title": "Project Schedule (Gantt Chart)",
            "completed": simulation.completion_percentage > 50,
            "download_url": f"/api/v1/simulations/{simulation_id}/artifacts/schedule.pdf" if simulation.completion_percentage > 50 else None
        },
        "budget_tracker": {
            "title": "Budget Tracking Spreadsheet",
            "completed": simulation.completion_percentage > 75,
            "download_url": f"/api/v1/simulations/{simulation_id}/artifacts/budget.xlsx" if simulation.completion_percentage > 75 else None
        }
    }
    
    return {
        "simulation_id": simulation_id,
        "simulation_title": simulation.title,
        "artifacts": artifacts,
        "total_artifacts": len(artifacts),
        "completed_artifacts": len([a for a in artifacts.values() if a["completed"]])
    }


@router.get("/stats/overview", response_model=SimulationStatsResponse)
async def get_simulation_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's simulation statistics."""
    # Get all user simulations
    result = await db.execute(
        select(ProjectSimulation)
        .where(ProjectSimulation.user_id == current_user.id)
    )
    simulations = result.scalars().all()
    
    # Calculate stats
    total_simulations = len(simulations)
    completed_simulations = len([s for s in simulations if s.status == SimulationStatus.COMPLETED])
    in_progress_simulations = len([s for s in simulations if s.status == SimulationStatus.IN_PROGRESS])
    
    # Calculate average scores
    completed_with_scores = [s for s in simulations if s.final_score is not None]
    average_score = (
        sum(s.final_score for s in completed_with_scores) / len(completed_with_scores)
    ) if completed_with_scores else None
    
    # Industry experience
    industries = {}
    for sim in simulations:
        industries[sim.industry] = industries.get(sim.industry, 0) + 1
    
    # Complexity levels completed
    complexity_stats = {}
    for sim in completed_simulations:
        level = f"Level {sim.complexity_level}"
        complexity_stats[level] = complexity_stats.get(level, 0) + 1
    
    return SimulationStatsResponse(
        total_simulations=total_simulations,
        completed_simulations=completed_simulations,
        in_progress_simulations=in_progress_simulations,
        average_score=round(average_score, 1) if average_score else None,
        industries_experienced=list(industries.keys()),
        complexity_levels_completed=complexity_stats,
        total_artifacts_created=sum(
            len(s.artifacts_created) if s.artifacts_created else 0 
            for s in simulations
        ),
        completion_rate=round(
            (completed_simulations / total_simulations * 100) if total_simulations > 0 else 0,
            1
        )
    )


@router.get("/{simulation_id}/skill-assessment", response_model=dict)
async def get_skill_assessment(
    simulation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get skill assessment results for a simulation."""
    result = await db.execute(
        select(ProjectSimulation)
        .where(and_(
            ProjectSimulation.id == simulation_id,
            ProjectSimulation.user_id == current_user.id
        ))
    )
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Mock skill assessment data
    skill_assessment = {
        "simulation_id": simulation_id,
        "simulation_title": simulation.title,
        "assessment_date": simulation.completed_at.isoformat() if simulation.completed_at else None,
        "overall_score": simulation.final_score,
        "skill_scores": {
            "leadership": 85,
            "communication": 78,
            "risk_management": 92,
            "stakeholder_management": 88,
            "time_management": 75,
            "budget_management": 82,
            "problem_solving": 90,
            "team_collaboration": 86
        },
        "strengths": [
            "Excellent risk identification and mitigation strategies",
            "Strong stakeholder engagement throughout the project",
            "Effective problem-solving during critical issues"
        ],
        "areas_for_improvement": [
            "Budget monitoring could be more frequent",
            "Communication with remote team members needs enhancement",
            "Time estimation accuracy for complex tasks"
        ],
        "recommended_learning": [
            "Advanced Budget Management for Project Managers",
            "Remote Team Communication Strategies",
            "Agile Estimation Techniques"
        ],
        "certificates_earned": [
            {
                "name": "Project Simulation Completion",
                "level": simulation.complexity_level,
                "download_url": f"/api/v1/simulations/{simulation_id}/certificate.pdf"
            }
        ] if simulation.status == SimulationStatus.COMPLETED else []
    }
    
    return skill_assessment

demo_router = APIRouter(
    prefix="/api/v1/demo/simulations",
    tags=["Demo Simulations"]
)


@demo_router.get("/{simulation_key}")
def load_demo_simulation(simulation_key: str):
    try:
        return load_simulation(simulation_key)
    except ValueError:
        raise HTTPException(status_code=404, detail="Demo simulation not found")


@demo_router.post("/{simulation_key}/action")
def run_demo_action(simulation_key: str, payload: dict):
    try:
        state = payload["state"]
        action_id = payload["action_id"]
        choice = payload["choice"]

        new_state, feedback, log = apply_action(state, action_id, choice)
        score = generate_score(new_state)
        coach_summary = generate_coach_summary(new_state, score)

        return {
            "state": new_state,
            "feedback": feedback,
            "log": log,
            "score": score,
            "coach_summary": coach_summary,
        }
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing key: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))