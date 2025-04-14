import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContactWithReviewerComponent } from './contact-with-reviewer.component';

describe('ContactWithReviewerComponent', () => {
  let component: ContactWithReviewerComponent;
  let fixture: ComponentFixture<ContactWithReviewerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContactWithReviewerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContactWithReviewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
