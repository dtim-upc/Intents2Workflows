import React from 'react'


type Props = {
  name: string
  size?: number
  type?: string
  extra_class?: string
  color?:string
}

export function Icon({ name, size = 18, type = "mdi", extra_class= "", color=""}: Props) {

  if (type === "mdi") {
    return (
      <i
        className={`${type} ${type}-${name} ui-icon ${extra_class}`}
        style={{ fontSize: size, color: color}}
        aria-hidden="true"
      />
    
    )
  }
  else {
    return (
      <i className={`material-icons ui-icon ${extra_class}`} 
      style={{ fontSize: size, color:color}}>
        {name}
      </i>
    )
  }
}

type Props2 = {
  children: React.ReactNode
  icon?: string
  iconSize?: number
  type?:string
  extra_class?:string
  extra_icon_class?:string
}

export function UI({ children, icon, iconSize = 18, extra_icon_class="", extra_class="" }: Props2) {
  return (
    <span className={`ui-inline ${extra_class}`} >
      {icon && (
        <span className="ui-icon-wrapper">
          <Icon name={icon} size={iconSize} extra_class={extra_icon_class}/>
        </span>
      )}
      <span className="ui-text">{children}</span>
    </span>
  )
}


export function Button({ children, icon, iconSize = 18, type = "mdi",  extra_icon_class="", extra_class="" }: Props2) {
  return (
    <span className={`button-inline ${extra_class}`}>
      {icon && (
        <span className="button-icon-wrapper">
          <Icon name={icon} size={iconSize} type={type} extra_class={extra_icon_class}/>
        </span>
      )}
      {children && (
        <span className="button-text">{children}</span>
      )}
    </span>
  )
}

