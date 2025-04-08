import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaymentRequestCustomerViewComponent } from './payment-request-customer-view.component';

describe('PaymentRequestCustomerViewComponent', () => {
  let component: PaymentRequestCustomerViewComponent;
  let fixture: ComponentFixture<PaymentRequestCustomerViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PaymentRequestCustomerViewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PaymentRequestCustomerViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
