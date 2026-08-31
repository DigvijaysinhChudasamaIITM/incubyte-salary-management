import { FormEvent, KeyboardEvent, ReactNode, useRef, useState } from "react";
import { X } from "lucide-react";

import {
  createEmployee,
  Employee,
  EmployeeApiError,
  EmployeeCreateInput,
} from "./api/employees";

const COUNTRIES = [
  ["CA", "Canada"],
  ["DE", "Germany"],
  ["GB", "United Kingdom"],
  ["IN", "India"],
  ["US", "United States"],
] as const;
const DEPARTMENTS = ["Engineering", "Finance", "Operations", "People", "Sales"];
type FieldName = keyof EmployeeCreateInput;
type FieldErrors = Partial<Record<FieldName, string>>;

export function EmployeeCreateDialog({
  currencies,
  currenciesLoading,
  currenciesError,
  onClose,
  onCreated,
}: {
  currencies: string[];
  currenciesLoading: boolean;
  currenciesError: boolean;
  onClose: () => void;
  onCreated: (employee: Employee) => void;
}) {
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState("");
  const submissionActive = useRef(false);

  function close() {
    if (!submissionActive.current) onClose();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") close();
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submissionActive.current) return;
    submissionActive.current = true;
    setSubmitting(true);
    setFieldErrors({});
    setFormError("");
    const values = new FormData(event.currentTarget);
    const input = Object.fromEntries(values.entries()) as unknown as EmployeeCreateInput;
    try {
      onCreated(await createEmployee(input));
    } catch (error) {
      const mapped = mapApiError(error);
      setFieldErrors(mapped.fields);
      setFormError(mapped.form);
      submissionActive.current = false;
      setSubmitting(false);
    }
  }

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={(event) => {
      if (event.target === event.currentTarget) close();
    }}>
      <div
        className="employee-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-employee-title"
        onKeyDown={handleKeyDown}
      >
        <div className="dialog-heading">
          <div>
            <p className="eyebrow">Employee directory</p>
            <h2 id="create-employee-title">Add employee</h2>
          </div>
          <button type="button" aria-label="Close add employee form" onClick={close} disabled={submitting}>
            <X size={18} aria-hidden="true" />
          </button>
        </div>

        <form onSubmit={submit}>
          <div className="form-grid">
            <Field label="Employee code" name="employee_code" error={fieldErrors.employee_code} autoFocus />
            <Field label="Name" name="name" error={fieldErrors.name} />
            <Field label="Email" name="email" type="email" error={fieldErrors.email} />
            <SelectField label="Country" name="country" error={fieldErrors.country}>
              <option value="">Select country</option>
              {COUNTRIES.map(([code, name]) => <option key={code} value={code}>{name}</option>)}
            </SelectField>
            <SelectField label="Department" name="department" error={fieldErrors.department}>
              <option value="">Select department</option>
              {DEPARTMENTS.map((department) => <option key={department}>{department}</option>)}
            </SelectField>
            <Field label="Job title" name="job_title" error={fieldErrors.job_title} />
            <Field
              label="Salary amount"
              name="salary_amount"
              type="number"
              step="0.01"
              min="0.01"
              error={fieldErrors.salary_amount}
            />
            <SelectField label="Currency" name="currency" error={fieldErrors.currency} disabled={currenciesLoading || currenciesError}>
              <option value="">{currenciesLoading ? "Loading currencies..." : "Select currency"}</option>
              {currencies.map((currency) => <option key={currency}>{currency}</option>)}
            </SelectField>
          </div>

          {currenciesError && <p className="form-error" role="alert">Supported currencies could not be loaded. Close the form and try again.</p>}
          {formError && <p className="form-error" role="alert">{formError}</p>}

          <div className="dialog-actions">
            <button type="button" className="secondary-button" onClick={close} disabled={submitting}>Cancel</button>
            <button type="submit" className="primary-button" disabled={submitting || currenciesLoading || currenciesError}>
              {submitting ? "Adding employee..." : "Add employee"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({ label, name, error, type = "text", ...inputProps }: {
  label: string;
  name: FieldName;
  error?: string;
  type?: string;
  autoFocus?: boolean;
  step?: string;
  min?: string;
}) {
  const errorId = `${name}-error`;
  return (
    <div className="form-control">
      <label htmlFor={name}>{label}</label>
      <input id={name} name={name} type={type} required aria-invalid={Boolean(error)} aria-describedby={error ? errorId : undefined} {...inputProps} />
      {error && <p id={errorId} className="field-error">{error}</p>}
    </div>
  );
}

function SelectField({ label, name, error, children, disabled = false }: {
  label: string;
  name: FieldName;
  error?: string;
  children: ReactNode;
  disabled?: boolean;
}) {
  const errorId = `${name}-error`;
  return (
    <div className="form-control">
      <label htmlFor={name}>{label}</label>
      <select id={name} name={name} required disabled={disabled} aria-invalid={Boolean(error)} aria-describedby={error ? errorId : undefined}>
        {children}
      </select>
      {error && <p id={errorId} className="field-error">{error}</p>}
    </div>
  );
}

function mapApiError(error: unknown): { fields: FieldErrors; form: string } {
  if (!(error instanceof EmployeeApiError)) {
    return { fields: {}, form: "Employee could not be created. Try again." };
  }
  const body = error.body as { detail?: unknown } | null;
  const detail = body?.detail;
  if (error.status === 409 && isObject(detail) && Array.isArray(detail.fields)) {
    return {
      fields: Object.fromEntries(detail.fields.map((field) => [field, `${field === "email" ? "Email" : "Employee code"} already exists.`])),
      form: "Resolve the duplicate value and try again.",
    };
  }
  if (error.status === 422 && isObject(detail) && detail.code === "unsupported_currency") {
    return { fields: { currency: "Select a supported currency." }, form: "" };
  }
  if (error.status === 422 && Array.isArray(detail)) {
    const fields: FieldErrors = {};
    for (const issue of detail) {
      if (isObject(issue) && Array.isArray(issue.loc)) {
        const field = issue.loc.at(-1);
        if (typeof field === "string" && typeof issue.msg === "string") {
          fields[field as FieldName] = issue.msg;
        }
      }
    }
    return { fields, form: "Correct the highlighted fields and try again." };
  }
  return { fields: {}, form: "Employee could not be created. Try again." };
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
