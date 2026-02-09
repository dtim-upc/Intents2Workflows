// src/components/StepList.tsx
import React from 'react'

type Step = {
  content: React.ReactNode  // now content can be any JSX/HTML
  icon?: React.ReactNode    // optional icon instead of number
}

type Props = {
  steps: Step[]
}

export function StepList({ steps }: Props) {
  return (
    <ol style={{ listStyle: 'none', padding: 0, margin: 0 }}>
      {steps.map((step, idx) => (
        <li
          key={idx}
          style={{
            display: 'flex',
            alignItems: 'stretch', // ⭐ IMPORTANT
            gap: 16,
            padding: '12px 16px',
            marginBottom: 12,
            borderRadius: 12,
          }}
        >
          {/* Number + vertical line */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              flexShrink: 0,
              minWidth: 32,
            }}
          >
            {/* Number circle */}
            <div className="step-circle"
            >
              {step.icon || idx + 1}
            </div>

            {/* Vertical line */}
            <div className='vertical-line'
            />
          </div>

          {/* Step content */}
          <div
            style={{
              flex: 1,
              lineHeight: 1.6,
              paddingTop: 4,
            }}
          >
            {step.content}
          </div>
        </li>
      ))}
    </ol>
  )
}
