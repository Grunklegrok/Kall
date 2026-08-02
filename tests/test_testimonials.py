from kall.models import Testimonial


def test_testimonial_defaults_private():
    item = Testimonial(
        user_id=1,
        author_name="Former Coworker",
        relationship="peer",
        body="A thoughtful and reliable collaborator.",
    )
    assert item.status == "pending_review"
    assert item.include_on_profile is False
    assert item.include_in_applications is False
    assert item.permission_granted is False


def test_permission_can_be_recorded():
    item = Testimonial(
        user_id=1,
        author_name="Former Manager",
        relationship="manager",
        body="Led the team through a difficult release.",
        permission_granted=True,
        verified_via_request=True,
    )
    assert item.permission_granted is True
    assert item.verified_via_request is True
