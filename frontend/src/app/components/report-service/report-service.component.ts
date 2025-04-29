import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { SupportService } from '../../services/support-service/support.service';

@Component({
  selector: 'app-report-service',
  templateUrl: './report-service.component.html',
  styleUrls: ['./report-service.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ]
})
export class ReportServiceComponent implements OnInit {
  reportForm: FormGroup;
  loading = false;
  error: string | null = null;
  success = false;

  constructor(
    private fb: FormBuilder,
    private supportService: SupportService,
    public dialogRef: MatDialogRef<ReportServiceComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { serviceId: number, serviceName: string }
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
    
    this.supportService.reportServiceProvider(this.data.serviceId, this.reportForm.value.reason)
      .subscribe({
        next: () => {
          this.loading = false;
          this.success = true;
          setTimeout(() => {
            this.dialogRef.close(true);
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
    this.dialogRef.close(false);
  }
}