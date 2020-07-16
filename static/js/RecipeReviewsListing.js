export default class RecipeReviewsListing {
    constructor(recipe_id) {
        this.recipe_id = recipe_id;
        this.init();
        this.reviewsContainer = document.getElementById(`recipe-reviews-container-${this.recipe_id}`)
    }
    async getReviews(args) {
        let queryString = new URLSearchParams(args).toString();
        const responseObj = await fetch(`/api/reviews/${this.recipe_id}/?${queryString}`);
        const reviews = await responseObj.json();
        console.log(reviews);
        return reviews;
    }
    renderReviewListing(review) {
        console.log(review);
        
        const reviewComment = document.createElement('div');
        reviewComment.classList.add('comment')
        
        const avatar = document.createElement('a');
        avatar.classList.add('avatar')
        
        const image = document.createElement('img');
        image.src = review.user.picture;
        
        avatar.append(image)

        const content = document.createElement('div');
        content.classList.add('content')

        const author = document.createElement('span');
        author.classList.add('author');
        author.innerText = review.user.name

        const metadata = document.createElement('div');
        metadata.classList.add('metadata')

        const rating = document.createElement('div');
        rating.classList.add('ui', 'small', 'yellow', 'star', 'rating', 'review-rating');
        rating.dataset['rating'] = review.rating;
        rating.dataset.maxRating = 5
        $(rating).rating('disable');

        metadata.append(rating)

        const text = document.createElement('div');
        text.classList.add('text');
        text.innerHTML = review.review_text;

        content.append(author, metadata, text)
        reviewComment.append(avatar,content)
        return reviewComment
    }
    init() {
        const _this = this;
        const filterBtn = document.querySelector('.filter-reviews');
        filterBtn.addEventListener('click', async function() {
            _this.reviewsContainer.classList.add('loading');
            const args = {
                rating: document.querySelector('input[name="rating"]').value,
                order_by: document.querySelector('input[name="order_by"]').value
            }
            const reviews = await _this.getReviews(args);
            if(reviews) {
                for(const review of reviews.reviews) {
                    const comment = _this.renderReviewListing(review)
                    _this.reviewsContainer.append(comment);
                }
            } else {

            }
            _this.reviewsContainer.classList.remove('loading');
        })
        $('.recipe-filter-dropdown').dropdown();
        $('.recipe-filter-dropdown[name="rating"]').dropdown('set selected', 'all');
        $('.recipe-filter-dropdown[name="order_by"]').dropdown('set selected', 'date');
    }
}