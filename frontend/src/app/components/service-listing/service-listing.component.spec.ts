import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiceListingComponent } from './service-listing.component';

describe('ServiceListingComponent', () => {
  let component: ServiceListingComponent;
  let fixture: ComponentFixture<ServiceListingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ServiceListingComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ServiceListingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
