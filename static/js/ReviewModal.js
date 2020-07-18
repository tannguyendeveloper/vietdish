import CurrentUser from './CurrentUser.js'

export default class ReviewModal {
    constructor(recipe_id) {
        this.id = recipe_id
        this.textAreaId = `review-text-${this.id}`
        this.modal;
        this.modalLink = document.querySelector(`.add-review-modal[data-recipe-id="${recipe_id}"]`);
        this.render()
    }
    render() {
        const _this = this;

        let modal = document.createElement('div');
        modal.id = `add-review-${this.id}`;
        modal.classList.add('ui','medium', 'modal');
        this.modal = modal;

        let header = document.createElement('div');
        header.classList.add('small', 'header', 'align-center');
        header.innerHTML = `Review for ${document.querySelector('h1.title').innerText}`;

        let content = document.createElement('div');
        content.classList.add('content');

        let ratingContainer = document.createElement('div');
        ratingContainer.classList.add('modal-rating-container');
        ratingContainer.innerHTML = '<label><strong>Your Rating:</strong><label> ';

        let rating = document.createElement('span');
        rating.id = `recipe-rating-${this.id}`;
        rating.classList.add('ui', 'yellow', 'star', 'rating' , 'review-rating');
        rating.dataset.maxRating = 5;

        let divider = document.createElement('div');
        divider.classList.add('ui', 'hidden', 'divider');

        let textArea = document.createElement('textarea');
        textArea.id = `review-text-${this.id}`
        textArea.name = 'review_text'

        let actions = document.createElement('div');
        actions.classList.add('actions');

        let cancelBtn = document.createElement('div')
        cancelBtn.classList.add('ui', 'deny', 'small', 'button');
        cancelBtn.innerHTML = '<i class="ban icon"></i> Cancel';
        this.cancelBtn = cancelBtn;

        let approveBtn = document.createElement('div')
        approveBtn.classList.add('ui', 'disabled', 'positive', 'small', 'button');
        approveBtn.innerHTML = '<i class="checkmark icon"></i> Submit';
        this.approveBtn = approveBtn;

        actions.append(cancelBtn, approveBtn);

        ratingContainer.append(rating);
        content.append(ratingContainer, divider, textArea);
        modal.append(header, content, actions);

        document.body.append(modal);
        
        this.initTinyMCE();
        this.initRating();
        this.initModal();
    }
    enableApproveButton() {
        this.approveBtn.classList.remove('disabled')
    }
    disableApproveButton() {
        this.approveBtn.classList.add('disabled')
    }
    isValid() {
        return this.rating && this.chars <= 500  && this.chars > 0 ? true : false
    }
    checkValid() {
        if(this.isValid()) {
            this.enableApproveButton();
        } else {
            this.disableApproveButton();
        }
    }
    async getReview() {
        const responseObj =  await fetch(`/api/reviews/${this.id}/?current_user=true`);
        const responseData = await responseObj.json();
        return responseData.data ? responseData.data : false
    }
    async submitReview() {
        const recipe_id = this.recipe_id;
        const data = {
            recipe_id: this.id,
            rating: this.rating,
            review_text: this.tinymce.get(this.textAreaId).getContent(),
        }
        return await fetch('/api/reviews/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
    }
    getTextAreaLength() {
        let body = this.tinymce.get(this.textAreaId).getBody(), text = this.tinymce.trim(body.innerText || body.textContent);
        return text.length
    }
    initRating() {
        const _this = this;
        $(`#recipe-rating-${this.id}`).rating({
            onRate: function() {
                _this.rating = $(this).rating('get rating')
                _this.chars = _this.getTextAreaLength();
                _this.checkValid();

            },
        })
    }
    initTinyMCE() {
        const _this = this;
        tinymce.init({
            selector: `#${this.textAreaId}`,
            toolbar: 'undo redo | bold italic underline | ',
            menubar: false,
            statusbar: false,
            setup: function(editor) {
                _this.tinymceEditor = editor;
                editor.on('keyup', function(e) {
                    _this.chars = _this.getTextAreaLength();
                    _this.checkValid();
                });
            }
        });
        this.tinymce = tinymce;
    }
    initModal() {
        const _this = this
        $(this.modal).modal({
            onApprove: async function() {
                const responseObj = await _this.submitReview();
                const response = await responseObj.json();
                let icon;
                if(_this.reviewPopup) _this.reviewPopup.updateReviewBreakdown();
                if(responseObj.status == 200) {
                    _this.modalLink.innerText = 'Edit Your Review';
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
            },
            onHidden: function() {
                _this.tinymceEditor.resetContent();
                $(`#recipe-rating-${_this.id}`).rating('clear rating')
            }
        })
    }
    async show() {
        const isAuthenticated = await CurrentUser.redirectIfNotAuthenticated();
        const review = await this.getReview();
        if(isAuthenticated) { 
            $(this.modal).modal('show')
        }
        if(review) {
            $(`#recipe-rating-${this.id}`).rating('set rating', review.rating);
            this.rating = review.rating;
            this.tinymce.get(this.textAreaId).setContent(review.review_text)
        }
    }
}