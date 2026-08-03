from kall.models.enums import WorkType
from kall.providers.jobs import DiscoveredJob
from kall.services.normalization import fingerprint, normalize_discovered


def test_fingerprint_ignores_tracking_query():
    a=DiscoveredJob("x","1","Acme","Director, Engineering","","https://a.test/job?utm=x")
    b=DiscoveredJob("y","2","Acme","Director, Engineering","","https://a.test/job?utm=y")
    assert fingerprint(a)==fingerprint(b)


def test_remote_and_salary_are_inferred():
    job=DiscoveredJob("x","1","Acme","Director","Remote US role paying $190,000 to $230,000","https://a.test/job","United States Remote")
    data=normalize_discovered(job)
    assert data["work_type"]==WorkType.REMOTE
    assert data["salary_min"]==190000
    assert data["salary_max"]==230000
