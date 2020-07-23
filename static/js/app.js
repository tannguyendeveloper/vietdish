import ReviewModal from './ReviewModal.js'
import ReviewsPopup from './ReviewsPopup.js'
import RecipeReviewsListing from './RecipeReviewsListing.js'
import CurrentUser from './CurrentUser.js'

$(document).ready(function() {

    const app = new VietDishApp();

})

class VietDishApp {
    constructor() {
        this.init();
    }
    init() {
        this.initSignUpModal();
        this.initFavoritesToggle();
        this.initReviewsPopup();
        this.initReviewModal();
        this.initRecipeReviewsListing();
        this.initRecipeTabMenu();
        this.initRecipeIngredientMeasurementToggle();
        this.initUserRatings();
        this.initPagination();
    }
    initSignUpModal() {
        const signUpModalLinks = document.querySelectorAll('.sign-up-modal');
        const signUpModal = document.querySelector('#sign-up-modal')
        if(signUpModalLinks && signUpModal) {
            for(const link of signUpModalLinks) {
                link.addEventListener('click', function() {
                    $(signUpModal).modal('show')
                })
            }
        }
    }
    initFavoritesToggle() {
        // Toggle Favorites
        const favoriteToggles = document.querySelectorAll('.favorite-toggle[data-recipe-id]');
        const toggleFavorite = async function(e) {
            const user_id = 1;
            const recipe_id = e.target.dataset.recipeId;
            const data = {user_id, recipe_id}
            CurrentUser.redirectIfNotAuthenticated()
            const responseObj = await fetch('/api/favorites/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            const response = await responseObj.json()
            let favoriteIcon = document.querySelectorAll(`.favorite-toggle[data-recipe-id="${recipe_id}"]`)
            let icon;
            if(responseObj.status == 200 && response.favorite) {
                for(let icon of favoriteIcon) {
                    icon.classList.add('red')
                    icon.classList.remove('grey')
                }
                icon = 'green check icon'
            } else if (responseObj.status == 200 && !response.favorite) {
                for(let icon of favoriteIcon) {
                    icon.classList.remove('red')
                    icon.classList.add('grey')
                }
                icon = 'green check icon'
            } else {
                icon = 'red ban icon'
            }
            $('body')
                .toast({
                    message: response.message ? response.message : 'Error',
                    displayTime: 2000,
                    position: 'bottom right',
                    showProgress: 'top',
                    showIcon: icon
                })
        }
        if(favoriteToggles) {
            for(let favorite of favoriteToggles) {
                favorite.addEventListener('click', toggleFavorite)
            }
        }
    }
    initReviewsPopup() {
        const _this = this;
        const reviewsPopupLinks = document.querySelectorAll('.reviews-popup-link[data-recipe-id]')
        if(reviewsPopupLinks) {
            this.reviewsPopups = {};
            for(let popupLink of reviewsPopupLinks) {
                const recipeId = popupLink.dataset.recipeId;
                const reviewsPopup = new ReviewsPopup(recipeId);
                this.reviewsPopups[recipeId] = reviewsPopup;
                $(popupLink).popup({
                    hoverable: true,
                    popup: $(`.ui.hidden.popup[data-recipe-id="${recipeId}"]`),
                    onShow: function(popup) {
                        reviewsPopup.updateReviewBreakdown();
                    }
                })
            }
        }
    }
    initUserRatings() {
        const _this = this;
        const userRatings = document.querySelectorAll('.user-rating');
        if(userRatings) {
            for(const rating of userRatings) {
                $(rating).rating('interactive', false);
                $(rating).rating('disable');
            }
        }
    }
    initReviewModal() {
        const reviewModalLink = document.querySelector('.add-review-modal');
        if(reviewModalLink) {
            const recipeId = reviewModalLink.dataset.recipeId;
            const modal = new ReviewModal(recipeId);
            modal.reviewPopup = this.reviewsPopups[`${recipeId}`] ? this.reviewsPopups[`${recipeId}`] : null;
            if(reviewModalLink) {
                reviewModalLink.addEventListener('click', function(e) {
                    modal.show()
                })
            }
        }
    }
    initRecipeReviewsListing() {
        const reviewsFilterForm = document.getElementById('reviews-filter-form');
        if(reviewsFilterForm) {
            const recipeId = reviewsFilterForm.dataset.recipeId;
            console.log(reviewsFilterForm)
            const recipeReviewsListing = new RecipeReviewsListing(recipeId);
            this.recipeReviewsListing = recipeReviewsListing
        }
    }
    initRecipeTabMenu() {
        const recipeTabMenu = document.querySelectorAll('#recipe-tabs .item')
        let recipeId = document.querySelector('#recipe-tabs .item[data-tab="reviews"]') ? document.querySelector('#recipe-tabs .item[data-tab="reviews"]').dataset.recipeId : null;
        if(recipeTabMenu && recipeId) {
            $(recipeTabMenu).tab({
                onFirstLoad: function(tab) {
                    if(tab === 'reviews') {
                        console.log(tab, recipeId)
                    }
                }
            })
            const urlParams = new URLSearchParams(window.location.search);
            if(urlParams.get('reviews')) {
                $(recipeTabMenu).tab('change tab', 'reviews')
                $(this.recipeReviewsListing.filterBtn).click()
            }
        }
    }
    initRecipeIngredientMeasurementToggle() {
        const measurementToggle = document.querySelectorAll('.measurement-toggle')
        if(measurementToggle) {
            $(measurementToggle)
            .checkbox({
                onChange: function() {
                    let unitOfMeasure = this.value;
                    $('span.ingredient-amount').each(function() {
                        let amount = $(this).data(`${unitOfMeasure}-amount`)
                        let unit =  $(this).data(`${unitOfMeasure}-unit`)
                        let text = `${amount} ${unit}`;
                        this.innerHTML = text;
                    })
                }
            })
        }
    }
    initPagination() {
        const pagination = document.querySelector('.recipe-pagination-dropdown')
        if(pagination) {
            const page = pagination.dataset.page;
            $(pagination).dropdown('set selected', page);
        }
    }
}
