from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)


class SkuCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price_cents: int = Field(ge=0)
    stock: int = Field(ge=0)


class FaqCreateRequest(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class SellingPointCreateRequest(BaseModel):
    text: str = Field(min_length=1)


class LiveSessionCreateRequest(BaseModel):
    product_id: str


class MockCommentRequest(BaseModel):
    content: str = Field(min_length=1)
    user: str = "观众"


class ReviewApproveRequest(BaseModel):
    reviewer_id: str = "operator"
    text: str | None = None


class ReviewRejectRequest(BaseModel):
    reviewer_id: str = "operator"
    reason: str = Field(min_length=1)


class ReviewRewriteRequest(BaseModel):
    reviewer_id: str = "operator"
    text: str = Field(min_length=1)


class ApiResponse(BaseModel):
    success: bool = True
    data: object | None = None
    error: object | None = None
