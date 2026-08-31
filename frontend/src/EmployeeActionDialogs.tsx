import { FormEvent, KeyboardEvent, ReactNode, useRef, useState } from "react";
import { X } from "lucide-react";

import {
  deactivateEmployee,
  Employee,
  EmployeeApiError,
  updateEmployeeSalary,
} from "./api/employees";

type DialogProps = {
  employee: Employee;
  onClose: () => void;
  onCompleted: (employee: Employee, action: "salary" | "deactivate") => void;
};

export function SalaryUpdateDialog({ employee, onClose, onCompleted }: DialogProps) {
  const [submitting, setSubmitting] = useState(false);
  const [salaryError, setSalaryError] = useState("");
  const [formError, setFormError] = useState("");
  const submissionActive = useRef(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submissionActive.current) return;
    submissionActive.current = true;
    setSubmitting(true);
    setSalaryError("");
    setFormError("");
    const salaryAmount = String(new FormData(event.currentTarget).get("salary_amount"));
    try {
      onCompleted(
        await updateEmployeeSalary(employee.employee_code, salaryAmount),
        "salary",
      );
    } catch (error) {
      const mapped = mutationError(error, "salary_amount");
      setSalaryError(mapped.field);
      setFormError(mapped.form);
      submissionActive.current = false;
      setSubmitting(false);
    }
  }

  return (
    <MutationDialog
      title="Update salary"
      closeLabel="Close salary update form"
      submitting={submitting}
      onClose={onClose}
    >
      <p className="dialog-context">
        {employee.name} · Current native salary: {formatSalary(employee)}
      </p>
      <form onSubmit={submit}>
        <div className="form-control">
          <label htmlFor="updated-salary">Salary amount ({employee.currency})</label>
          <input
            id="updated-salary"
            name="salary_amount"
            type="number"
            min="0.01"
            step="0.01"
            defaultValue={employee.salary_amount}
            required
            autoFocus
            aria-invalid={Boolean(salaryError)}
            aria-describedby={salaryError ? "updated-salary-error" : undefined}
          />
          {salaryError && <p id="updated-salary-error" className="field-error">{salaryError}</p>}
        </div>
        {formError && <p className="form-error" role="alert">{formError}</p>}
        <div className="dialog-actions">
          <button type="button" className="secondary-button" onClick={onClose} disabled={submitting}>Cancel</button>
          <button type="submit" className="primary-button" disabled={submitting}>
            {submitting ? "Updating salary..." : "Update salary"}
          </button>
        </div>
      </form>
    </MutationDialog>
  );
}

export function DeactivateEmployeeDialog({ employee, onClose, onCompleted }: DialogProps) {
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");
  const submissionActive = useRef(false);

  async function deactivate() {
    if (submissionActive.current) return;
    submissionActive.current = true;
    setSubmitting(true);
    setFormError("");
    try {
      onCompleted(await deactivateEmployee(employee.employee_code), "deactivate");
    } catch (error) {
      setFormError(mutationError(error).form);
      submissionActive.current = false;
      setSubmitting(false);
    }
  }

  return (
    <MutationDialog
      title="Deactivate employee"
      closeLabel="Close employee deactivation confirmation"
      submitting={submitting}
      onClose={onClose}
    >
      <div className="confirmation-copy">
        <p>Deactivate <strong>{employee.name}</strong> ({employee.employee_code})?</p>
        <p>The record will be retained, but the employee will be excluded from current payroll.</p>
      </div>
      {formError && <p className="form-error" role="alert">{formError}</p>}
      <div className="dialog-actions">
        <button type="button" className="secondary-button" onClick={onClose} disabled={submitting}>Cancel</button>
        <button type="button" className="danger-button" onClick={deactivate} disabled={submitting} autoFocus>
          {submitting ? "Deactivating employee..." : "Deactivate employee"}
        </button>
      </div>
    </MutationDialog>
  );
}

function MutationDialog({ title, closeLabel, submitting, onClose, children }: {
  title: string;
  closeLabel: string;
  submitting: boolean;
  onClose: () => void;
  children: ReactNode;
}) {
  function close() {
    if (!submitting) onClose();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") close();
  }

  const titleId = `employee-action-${title.toLowerCase().replaceAll(" ", "-")}`;
  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={(event) => {
      if (event.target === event.currentTarget) close();
    }}>
      <div className="employee-dialog action-dialog" role="dialog" aria-modal="true" aria-labelledby={titleId} onKeyDown={handleKeyDown}>
        <div className="dialog-heading">
          <div>
            <p className="eyebrow">Employee directory</p>
            <h2 id={titleId}>{title}</h2>
          </div>
          <button type="button" aria-label={closeLabel} onClick={close} disabled={submitting}>
            <X size={18} aria-hidden="true" />
          </button>
        </div>
        <div className="action-dialog-body">{children}</div>
      </div>
    </div>
  );
}

function mutationError(error: unknown, fieldName?: string): { field: string; form: string } {
  if (!(error instanceof EmployeeApiError)) {
    return { field: "", form: "The employee action could not be completed. Try again." };
  }
  const detail = (error.body as { detail?: unknown } | null)?.detail;
  if (error.status === 422 && Array.isArray(detail) && fieldName) {
    const issue = detail.find(
      (item) => isObject(item) && Array.isArray(item.loc) && item.loc.at(-1) === fieldName,
    );
    return {
      field: isObject(issue) && typeof issue.msg === "string" ? issue.msg : "Enter a valid positive salary.",
      form: "",
    };
  }
  if (error.status === 409 && isObject(detail) && detail.code === "employee_inactive") {
    return { field: "", form: "Salary cannot be updated for an inactive employee." };
  }
  if (error.status === 404) {
    return { field: "", form: "This employee no longer exists." };
  }
  return { field: "", form: "The employee action could not be completed. Try again." };
}

function formatSalary(employee: Employee): string {
  return `${employee.currency} ${employee.salary_amount}`;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
