{{ range .Versions }}
<a name="{{ .Tag.Name }}"></a>
## {{ if .Tag.Previous }}[{{ .Tag.Name }}]({{ $.Info.RepositoryURL }}/compare/{{ .Tag.Previous.Name }}...{{ .Tag.Name }}){{ else }}{{ .Tag.Name }}{{ end }} ({{ datetime "2006-01-02" .Tag.Date }})

{{ range .Commits -}}
{{ if not (contains .Type "[") }}- {{.Hash.Short}} {{ .Subject }}
{{ if not (eq (len .Body) 0) }}{{ .Body }}{{ end }}
{{ range .Refs -}}
{{ " " }} - #{{ .Ref }}
{{ end }}
{{ end }}
{{ end }}

{{ end -}}
