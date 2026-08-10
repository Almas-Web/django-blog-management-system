import pytest
from rest_framework.test import APIClient

from blog.models import Blog
from unittest.mock import patch


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )


@pytest.fixture
def other_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="TestPassword123",
    )


@pytest.fixture
def blog(user):
    return Blog.objects.create(
        title="Test Blog",
        content="This is test blog content.",
        author=user,
    )


# CREATE BLOG

@pytest.mark.django_db
def test_create_blog(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/blogs/create/",
        {
            "title": "New Blog",
            "content": "This is a new blog.",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["title"] == "New Blog"

    assert Blog.objects.filter(
        title="New Blog",
        author=user,
    ).exists()


# LIST BLOGS

@pytest.mark.django_db
def test_list_blogs(api_client, blog):
    response = api_client.get("/api/blogs/")

    assert response.status_code == 200


# BLOG DETAIL

@pytest.mark.django_db
def test_blog_detail(api_client, blog):
    response = api_client.get(
        f"/api/blogs/{blog.id}/"
    )

    assert response.status_code == 200
    assert response.data["title"] == blog.title


# UPDATE OWN BLOG

@pytest.mark.django_db
def test_update_own_blog(api_client, user, blog):
    api_client.force_authenticate(user=user)

    response = api_client.put(
        f"/api/blogs/{blog.id}/update/",
        {
            "title": "Updated Blog",
            "content": "Updated content.",
        },
        format="json",
    )

    assert response.status_code == 200

    blog.refresh_from_db()

    assert blog.title == "Updated Blog"
    assert blog.content == "Updated content."


# DELETE OWN BLOG

@pytest.mark.django_db
def test_delete_own_blog(api_client, user, blog):
    api_client.force_authenticate(user=user)

    response = api_client.delete(
        f"/api/blogs/{blog.id}/delete/"
    )

    assert response.status_code == 204

    assert not Blog.objects.filter(
        id=blog.id
    ).exists()


# MY BLOGS

@pytest.mark.django_db
def test_my_blogs(api_client, user, blog):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/blogs/my-blogs/"
    )

    assert response.status_code == 200

# BLOG PERMISSIONS

@pytest.mark.django_db
def test_other_user_cannot_update_blog(api_client, other_user, blog):
    api_client.force_authenticate(user=other_user)

    response = api_client.put(
        f"/api/blogs/{blog.id}/update/",
        {
            "title": "Hacked Blog",
            "content": "Someone else's content.",
        },
        format="json",
    )

    assert response.status_code == 403

    blog.refresh_from_db()
    assert blog.title == "Test Blog"


@pytest.mark.django_db
def test_other_user_cannot_delete_blog(api_client, other_user, blog):
    api_client.force_authenticate(user=other_user)

    response = api_client.delete(
        f"/api/blogs/{blog.id}/delete/"
    )

    assert response.status_code == 403

    assert Blog.objects.filter(id=blog.id).exists()


@pytest.mark.django_db
def test_unauthenticated_cannot_create_blog(api_client):
    response = api_client.post(
        "/api/blogs/create/",
        {
            "title": "Unauthorized Blog",
            "content": "This should not be created.",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_cannot_update_blog(api_client, blog):
    response = api_client.put(
        f"/api/blogs/{blog.id}/update/",
        {
            "title": "Unauthorized Update",
            "content": "This should not work.",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_cannot_delete_blog(api_client, blog):
    response = api_client.delete(
        f"/api/blogs/{blog.id}/delete/"
    )

    assert response.status_code == 401

    assert Blog.objects.filter(id=blog.id).exists()
@pytest.mark.django_db
def test_blog_search(api_client, user):
    Blog.objects.create(
        title="Django Tutorial",
        content="Learn Django REST Framework",
        author=user,
    )

    Blog.objects.create(
        title="Python Guide",
        content="Learn Python programming",
        author=user,
    )

    response = api_client.get(
        "/api/blogs/?search=Django"
    )

    assert response.status_code == 200

    # Paginated response
    results = response.data["results"]

    assert len(results) == 1
    assert results[0]["title"] == "Django Tutorial"


@pytest.mark.django_db
def test_blog_filter_by_author(api_client, user, other_user):
    Blog.objects.create(
        title="User Blog 1",
        content="Content 1",
        author=user,
    )

    Blog.objects.create(
        title="User Blog 2",
        content="Content 2",
        author=user,
    )

    Blog.objects.create(
        title="Other User Blog",
        content="Content 3",
        author=other_user,
    )

    response = api_client.get(
        f"/api/blogs/?author={user.id}"
    )

    assert response.status_code == 200

    results = response.data["results"]

    assert len(results) == 2

    for blog in results:
        assert blog["author"] == user.id

@pytest.mark.django_db
def test_blog_ordering_by_title(api_client, user):
    Blog.objects.create(
        title="Zebra Blog",
        content="Content Z",
        author=user,
    )

    Blog.objects.create(
        title="Apple Blog",
        content="Content A",
        author=user,
    )

    Blog.objects.create(
        title="Middle Blog",
        content="Content M",
        author=user,
    )

    # Ascending
    response = api_client.get(
        "/api/blogs/?ordering=title"
    )

    assert response.status_code == 200

    results = response.data["results"]

    titles = [blog["title"] for blog in results]

    assert titles == [
        "Apple Blog",
        "Middle Blog",
        "Zebra Blog",
    ]

    # Descending
    response = api_client.get(
        "/api/blogs/?ordering=-title"
    )

    assert response.status_code == 200

    results = response.data["results"]

    titles = [blog["title"] for blog in results]

    assert titles == [
        "Zebra Blog",
        "Middle Blog",
        "Apple Blog",
    ]

@pytest.mark.django_db
def test_blog_pagination(api_client, user):
    # Create 7 blogs
    for i in range(7):
        Blog.objects.create(
            title=f"Blog {i}",
            content=f"Content {i}",
            author=user,
        )

    # Default page size = 5
    response = api_client.get("/api/blogs/")

    assert response.status_code == 200

    assert response.data["count"] == 7
    assert len(response.data["results"]) == 5

    # Page 2
    response = api_client.get(
        "/api/blogs/?page=2"
    )

    assert response.status_code == 200

    assert len(response.data["results"]) == 2

    # Custom page size
    response = api_client.get(
        "/api/blogs/?page_size=3"
    )

    assert response.status_code == 200
    assert len(response.data["results"]) == 3

    # max_page_size = 10
    response = api_client.get(
        "/api/blogs/?page_size=20"
    )

    assert response.status_code == 200

    # Maximum should be limited to 10
    assert len(response.data["results"]) == 7

@pytest.mark.django_db
def test_blog_detail_invalid_id(api_client):
    response = api_client.get(
        "/api/blogs/99999/"
    )

    assert response.status_code == 404
@pytest.mark.django_db
def test_create_blog_missing_required_fields(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/blogs/create/",
        {},
        format="json",
    )

    assert response.status_code == 400

    assert "title" in response.data
    assert "content" in response.data
@pytest.mark.django_db
def test_create_blog_invalid_data(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/blogs/create/",
        {
            "title": "A" * 256,
            "content": "Valid content",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "title" in response.data
# BLOG SUMMARY - LLM

@pytest.mark.django_db
@patch("blog.views.LLMService")
def test_blog_summary(mock_llm_service, api_client, user, blog):
    api_client.force_authenticate(user=user)

    mock_llm_service.return_value.generate.return_value = (
        "This is a summarized version of the blog."
    )

    response = api_client.post(
        f"/api/blogs/{blog.id}/summarize/"
    )

    assert response.status_code == 200
    assert response.data["summary"] == (
        "This is a summarized version of the blog."
    )

    mock_llm_service.return_value.generate.assert_called_once()


@pytest.mark.django_db
def test_unauthenticated_cannot_summarize_blog(api_client, blog):
    response = api_client.post(
        f"/api/blogs/{blog.id}/summarize/"
    )

    assert response.status_code == 401


@pytest.mark.django_db
@patch("blog.views.LLMService")
def test_blog_summary_sends_blog_data_to_llm(
    mock_llm_service,
    api_client,
    user,
    blog,
):
    api_client.force_authenticate(user=user)

    mock_llm_service.return_value.generate.return_value = "Test summary"

    response = api_client.post(
        f"/api/blogs/{blog.id}/summarize/"
    )

    assert response.status_code == 200

    # Get the prompt sent to LLM
    prompt = mock_llm_service.return_value.generate.call_args[0][0]

    assert blog.title in prompt
    assert blog.content in prompt
    assert "Return only the summary." in prompt