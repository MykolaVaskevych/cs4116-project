import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomerToCustomerComponent } from './customer-to-customer.component';

describe('CustomerToCustomerComponent', () => {
  let component: CustomerToCustomerComponent;
  let fixture: ComponentFixture<CustomerToCustomerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CustomerToCustomerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CustomerToCustomerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
