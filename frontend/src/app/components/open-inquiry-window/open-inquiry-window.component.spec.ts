import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OpenInquiryWindowComponent } from './open-inquiry-window.component';

describe('OpenInquiryWindowComponent', () => {
  let component: OpenInquiryWindowComponent;
  let fixture: ComponentFixture<OpenInquiryWindowComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OpenInquiryWindowComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OpenInquiryWindowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
