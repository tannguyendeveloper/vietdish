export default class RecipeReviewsListing {
    constructor(recipe_id) {
        this.recipe_id = recipe_id;
        this.init();
    }
    async getReviews(args) {
        let queryString = new URLSearchParams(args).toString();
        const response = await fetch(`/api/reviews/${this.recipe_id}/?${queryString}`);
        console.log(response);
    }
    init() {
        const _this = this;
        const filterBtn = document.querySelector('.filter-reviews');
        filterBtn.addEventListener('click', async function() {
            const args = {
                rating: document.querySelector('input[name="rating"]').value,
                order_by: document.querySelector('input[name="order_by"]').value
            }
            console.log(args);
            results = await _this.getReviews(args);
            console.log(results)
        })
        $('.recipe-filter-dropdown').dropdown();
        $('.recipe-filter-dropdown[name="rating"]').dropdown('set selected', 'all');
        $('.recipe-filter-dropdown[name="order_by"]').dropdown('set selected', 'date');
    }
}