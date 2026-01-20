"""Tests for experience tools."""

from app.tools.experience import (
    get_professional_experience,
    get_latest_experience,
    get_skills,
    get_projects,
    get_education,
    get_profile,
    PROFILE,
    EXPERIENCES,
    SKILLS,
    PROJECTS,
    EDUCATION,
)


def test_profile_data():
    """Test that profile data is properly defined."""
    assert PROFILE.name == "George Dekermenjian"
    assert "Director" in PROFILE.title
    assert PROFILE.email is not None
    assert PROFILE.location is not None


def test_experiences_data():
    """Test that experiences data is properly defined."""
    assert len(EXPERIENCES) > 0
    # Check first experience has required fields
    exp = EXPERIENCES[0]
    assert exp.company is not None
    assert exp.title is not None
    assert exp.period is not None


def test_skills_data():
    """Test that skills data is properly defined."""
    assert len(SKILLS) > 0
    # Check skills have category and items
    for skill in SKILLS:
        assert skill.category is not None
        assert len(skill.skills) > 0


def test_projects_data():
    """Test that projects data is properly defined."""
    assert len(PROJECTS) > 0
    # Check first project has required fields
    proj = PROJECTS[0]
    assert proj.name is not None
    assert proj.description is not None


def test_education_data():
    """Test that education data is properly defined."""
    assert len(EDUCATION) > 0
    # Check education has required fields
    edu = EDUCATION[0]
    assert edu.institution is not None
    assert edu.degree is not None


def test_get_professional_experience():
    """Test get_professional_experience tool returns all experiences."""
    result = get_professional_experience()
    assert len(result.experiences) == len(EXPERIENCES)
    assert result.summary is not None
    # Check first experience is Fundcraft
    assert result.experiences[0].company == "Fundcraft"


def test_get_latest_experience():
    """Test get_latest_experience tool returns most recent role only."""
    result = get_latest_experience()
    # Should return one experience
    assert result.experience is not None
    # Should be the most recent (Fundcraft)
    assert result.experience.company == EXPERIENCES[0].company
    assert result.summary is not None


def test_get_skills():
    """Test get_skills tool returns skills list."""
    result = get_skills()
    assert len(result.skills) == len(SKILLS)
    assert result.summary is not None


def test_get_projects():
    """Test get_projects tool returns projects."""
    result = get_projects()
    assert len(result.projects) == len(PROJECTS)
    assert result.summary is not None


def test_get_education():
    """Test get_education tool returns education."""
    result = get_education()
    assert len(result.education) == len(EDUCATION)
    assert result.summary is not None


def test_get_profile():
    """Test get_profile tool returns profile info."""
    result = get_profile()
    assert result.profile.name == PROFILE.name
    assert result.profile.title is not None
    assert result.profile.email is not None
