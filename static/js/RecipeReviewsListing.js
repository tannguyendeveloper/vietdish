export default class RecipeReviewsListing {
    constructor(recipe_id) {
        this.recipe_id = recipe_id;
        this.reviewsContainer = document.getElementById(`recipe-reviews-container-${this.recipe_id}`)
        this.filterBtn = document.querySelector('.filter-reviews');
        this.loadMoreBtn = document.querySelector('#load-more-btn');
        this.init();
    }
    async getReviews(args) {
        let queryString = new URLSearchParams(args).toString();
        const responseObj = await fetch(`/api/reviews/${this.recipe_id}/?${queryString}`);
        const reviews = await responseObj.json();
        return reviews;
    }
    renderReviewListing(review) {
        console.log(review);

        const reviewComment = document.createElement('div');
        reviewComment.classList.add('comment');

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

        const date = document.createElement('div');
        date.classList.add('date');
        date.innerHTML = review.date_created;

        metadata.append(date)

        const text = document.createElement('div');
        text.classList.add('text');
        text.innerHTML = review.review_text;

        content.append(rating, author, metadata, text)
        reviewComment.append(avatar,content)
        return reviewComment
    }
    loadMoreButton(data) {
        if(data.current_page !== data.pages  && data.pages > 1) {
            this.loadMoreBtn.dataset['rating'] = data.rating;
            this.loadMoreBtn.dataset['order_by'] = data.order_by;
            this.loadMoreBtn.dataset['page'] = parseInt(data.current_page) + 1;
            this.loadMoreBtn.innerText = 'Load More Reviews';
            this.loadMoreBtn.style.display = 'inline-block';
        } else {
            this.loadMoreBtn.dataset['rating'] = 'all';
            this.loadMoreBtn.dataset['order_by'] = 'date';
            this.loadMoreBtn.dataset['page'] = 1;
            this.loadMoreBtn.innerText = 'Load Reviews';
            this.loadMoreBtn.style.display = 'none';
        }
    }
    async handleGetReviews(args) {
        this.reviewsContainer.classList.add('loading');
        const data = await this.getReviews(args);
        if(data.reviews) {
            for(const review of data.reviews) {
                const comment = this.renderReviewListing(review)
                this.reviewsContainer.append(comment);
            }
        } else {
            this.reviewsContainer.innerHTML = '<p class="ui error message">No reviews found.</p>';
        }
        this.loadMoreButton(data);
        this.reviewsContainer.classList.remove('loading');
    }
    init() {
        const _this = this;
        this.filterBtn.addEventListener('click', async function() {
            const args = {
                rating: document.querySelector('input[name="rating"]').value,
                order_by: document.querySelector('input[name="order_by"]').value
            }
            _this.reviewsContainer.innerHTML = '';
            _this.handleGetReviews(args);
        })
        this.loadMoreBtn.addEventListener('click', async function() {
            const args = {
                rating: _this.loadMoreBtn.dataset.rating,
                order_by: _this.loadMoreBtn.dataset.orderBy,
                page: _this.loadMoreBtn.dataset.page
            }
            _this.handleGetReviews(args);
        })
        $('.recipe-filter-dropdown').dropdown();
        $('.recipe-filter-dropdown[name="rating"]').dropdown('set selected', 'all');
        $('.recipe-filter-dropdown[name="order_by"]').dropdown('set selected', 'date');
    }
}
