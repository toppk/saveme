-- Horizon's pandoc filter.

-- Wide tables scroll inside their own frame.
function Table(t)
  return pandoc.Div({ t }, pandoc.Attr("", { "table-wrap" }))
end

-- In a `::: tier` row, each `[text]{.box}` span becomes a box of its own.
function Div(d)
  if not d.classes:includes("tier") then
    return nil
  end
  local boxes = {}
  for _, block in ipairs(d.content) do
    if block.t == "Para" or block.t == "Plain" then
      for _, inline in ipairs(block.content) do
        if inline.t == "Span" then
          table.insert(boxes, pandoc.Div({ pandoc.Plain(inline.content) }, inline.attr))
        end
      end
    else
      table.insert(boxes, block)
    end
  end
  d.content = boxes
  return d
end
