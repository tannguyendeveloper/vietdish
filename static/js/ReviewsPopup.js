export default class ReviewsPopup {
    constructor(id) {
        this.recipe_id = id;
        this.render();
    }
    renderReviewBreakdownRow(i, pct) {
        const breakDownRow = document.createElement('div');
        breakDownRow.classList.add('breakdown-row');
        const breakdown = document.createElement('div');
        breakdown.classList.add('ui', 'mini', 'yellow', 'star', 'rating', 'breakdown');
        breakdown.dataset.recipeId = this.recipe_id;
        breakdown.dataset.maxRating = i;
        breakdown.dataset.rating = i;
        
        const ratingCountPercent = document.createElement('div');
        ratingCountPercent.innerHTML = pct;
        ratingCountPercent.classList.add('rating-count-percent');
        breakDownRow.append(breakdown, ratingCountPercent);
        return breakDownRow;
    }
    async getReviewBreakdown() {
        this.content.classList.add('loading')
        const response = await fetch(`/api/reviews/${this.recipe_id}/?count=true`);
        const responseJson = await response.json();
        return responseJson.data ? responseJson.data : false;
    }
    async updateReviewBreakdown() {
        const ratingObj = await this.getReviewBreakdown();
        const reviewsPopupLinkContainer = document.querySelector(`.reviews-popup-link-container[data-recipe-id="${this.recipe_id}"]`);
        const reviewsPopupLink = document.querySelector(`.reviews-popup-link[data-recipe-id="${this.recipe_id}"]`);
        const ratingAvg = document.querySelector(`.reviews-popup-link-container[data-recipe-id="${this.recipe_id}"] .rating-avg`);
        if(ratingObj) {
            let popUpLinkInnerHTML;
            const userRating = document.querySelector(`.user-rating[data-recipe-id="${this.recipe_id}"]`)
            if(userRating.dataset.rating  != ratingObj.avg) { 
                $(userRating).rating('set rating', ratingObj.avg);
            }
            if(ratingObj.count != 0) {
                this.breakdownContainer.innerHTML = '';
                for(let i = 5; i > 0; i--) {
                    reviewsPopupLinkContainer.dataset[`stars-${i}`] = ratingObj.ratings[i]
                    this.breakdownContainer.append(this.renderReviewBreakdownRow(i, `${(ratingObj.ratings[i]/ratingObj.count) * 100}%`))
                }
                $(`.breakdown[data-recipe-id="${this.recipe_id}"]`).rating('disable');
                ratingAvg.innerHTML = `${ratingObj.avg.toFixed(1)} from `;
                reviewsPopupLink.innerHTML = `${ratingObj.count} reviews`;
            } else {
                ratingAvg.innerHTML = ''
            }
        } else {
            this.breakdownContainer.innerHTML = 'No reviews yet'
        }
        this.content.classList.remove('loading')
    }
    async render() {
        const popup = document.createElement('div');
        popup.classList.add('ui','hidden','popup');
        popup.dataset.recipeId = this.recipe_id;

        const content = document.createElement('div');
        content.classList.add('content', 'ui', 'basic', 'segment', 'rating-content');
        this.content = content;

        const header = document.createElement('strong');
        header.innerText = 'Reviews';

        const divider = document.createElement('div');
        divider.classList.add('ui', 'divider');

        const reviewsBreakdownContainer = document.createElement('div')
        reviewsBreakdownContainer.classList.add('rating-breakdown')
        reviewsBreakdownContainer.dataset.recipeId = this.recipe_id;
        this.breakdownContainer = reviewsBreakdownContainer;

        content.append(header, divider, reviewsBreakdownContainer);
        popup.append(content)
        document.body.append(popup)
    }
}