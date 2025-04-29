import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { SupportService } from '../../services/support-service/support.service';

@Component({
  selector: 'app-report-service',
  templateUrl: './report-service.component.html',
  styleUrls: ['./report-service.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ]
})
export class ReportServiceComponent implements OnInit {
  reportForm: FormGroup;
  loading = false;
  error: string | null = null;
  success = false;
  
  @Input() serviceId!: number;
  @Input() serviceName!: string;

  constructor(
    private fb: FormBuilder,
    private supportService: SupportService,
    public activeModal: NgbActiveModal
  ) {
    this.reportForm = this.fb.group({
      reason: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(500)]]
    });
  }

  ngOnInit(): void {
  }

  onSubmit(): void {
    if (this.reportForm.invalid) return;
    
    this.loading = true;
    this.error = null;
    
    this.supportService.reportServiceProvider(this.serviceId, this.reportForm.value.reason)
      .subscribe({
        next: () => {
          this.loading = false;
          this.success = true;
          setTimeout(() => {
            this.activeModal.close(true);
          }, 1500);
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 'Failed to submit report. Please try again.';
          console.error(err);
        }
      });
  }

  onCancel(): void {
    this.activeModal.dismiss('cancel');
  }
}