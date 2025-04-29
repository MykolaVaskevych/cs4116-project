import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-review-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="modal-header">
      <h4 class="modal-title">{{ isEditing ? 'Edit Your Review' : 'Leave a Review' }}</h4>
      <button type="button" class="btn-close" aria-label="Close" (click)="activeModal.dismiss('Cross click')"></button>
    </div>
    <div class="modal-body">
      <form [formGroup]="reviewForm">
        <div class="form-group mb-3">
          <label for="rating">Rating</label>
          <select class="form-select" id="rating" formControlName="rating" required>
            <option value="5">★★★★★ (5/5) Excellent</option>
            <option value="4">★★★★☆ (4/5) Very Good</option>
            <option value="3">★★★☆☆ (3/5) Average</option>
            <option value="2">★★☆☆☆ (2/5) Poor</option>
            <option value="1">★☆☆☆☆ (1/5) Very Poor</option>
          </select>
          <div *ngIf="reviewForm.get('rating')?.invalid && (reviewForm.get('rating')?.dirty || reviewForm.get('rating')?.touched)" class="text-danger">
            Rating is required
          </div>
        </div>
        <div class="form-group">
          <label for="comment">Comment (Optional)</label>
          <textarea class="form-control" id="comment" formControlName="comment" rows="3"></textarea>
        </div>
      </form>
    </div>
    <div class="modal-footer">
      <button type="button" class="btn btn-secondary" (click)="activeModal.dismiss('Cancel')">Cancel</button>
      <button type="button" class="btn btn-primary" [disabled]="reviewForm.invalid" (click)="submitReview()">
        {{ isEditing ? 'Update Review' : 'Submit Review' }}
      </button>
    </div>
  `,
  styles: [`
    .form-group { margin-bottom: 15px; }
    .text-danger { color: #dc3545; font-size: 0.875rem; margin-top: 5px; }
  `]
})
export class ReviewFormComponent implements OnInit {
  @Input() serviceId: any;
  @Input() isEditing: boolean = false;
  @Input() reviewId: number | null = null;
  @Input() existingRating: number = 5;
  @Input() existingComment: string = '';
  @Output() reviewSubmitted = new EventEmitter<{rating: number, comment: string}>();

  reviewForm: FormGroup;

  constructor(
    public activeModal: NgbActiveModal,
    private fb: FormBuilder
  ) {
    this.reviewForm = this.fb.group({
      rating: [5, Validators.required],
      comment: ['']
    });
  }
  
  ngOnInit() {
    // If editing, pre-fill the form with existing review data
    if (this.isEditing) {
      this.reviewForm.patchValue({
        rating: this.existingRating,
        comment: this.existingComment
      });
    }
  }

  submitReview() {
    if (this.reviewForm.valid) {
      const { rating, comment } = this.reviewForm.value;
      this.reviewSubmitted.emit({ rating, comment });
      this.activeModal.close();
    }
  }
}