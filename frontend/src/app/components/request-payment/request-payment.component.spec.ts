import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestPaymentComponent } from './request-payment.component';

describe('RequestPaymentComponent', () => {
  let component: RequestPaymentComponent;
  let fixture: ComponentFixture<RequestPaymentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RequestPaymentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RequestPaymentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
