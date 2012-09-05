import sublime, sublime_plugin

class MakeBlockCommand(sublime_plugin.TextCommand):
    def run(self, edit, forward = 1):

        view = self.view

        # store selection retions
        regions = [region for region in view.sel()]
        view.sel().clear()

        # prepare list of new selection regions
        newRegions = []

        # handle each region individually
        for region in regions:

            # try to make region on future block content
            if region.empty():

                # find line range
                line = view.line(region.begin())

                # expand region to eol
                region = sublime.Region(region.begin(), line.end())

                # if empty to end of line, use next line
                if len(view.substr(region).strip()) == 0:

                    # translate position to row
                    row, _ = view.rowcol(region.begin())

                    # get next row region
                    nextLine = view.line(view.text_point(row + 1, 0))

                    # make region from current position to end of next row
                    region = sublime.Region(region.begin(), nextLine.end())

            beg = region.begin()
            end = region.end()

            # ignore any leading spaces
            while view.substr(beg) == " ":
                beg += 1

            # insert space if there is no whitespace
            if not view.substr(beg-1).isspace():
                view.insert(edit, beg, " ")
                beg += 1
                end += 1

            # insert opening bracket
            view.insert(edit, beg, "{")
            beg += 1
            end += 1

            # check if there is text to eol
            line = view.line(beg)
            if len(view.substr(sublime.Region(beg, line.end())).strip()) > 0:
                # use text in this line as block content
                view.insert(edit, beg, "\n")
                beg += 1
                end += 1
            else:
                # the block content begins at next line
                row, _ = view.rowcol(beg)
                beg = view.text_point(row+1, 0)

            # remember row numbers
            firstRow, _ = view.rowcol(beg)
            lastRow, _ = view.rowcol(end)

            # insert block closing bracket
            view.insert(edit, end, "\n}")

            # make some indendation fixes
            view.sel().add(sublime.Region(beg, end+2))
            view.run_command("reindent", { "single_line": 1 })
            view.sel().clear()

            # insert additional newline at end or beggining of block
            if forward:
                pos = view.line(view.text_point(lastRow, 0)).end()
                view.insert(edit, pos, "\n")
                pos += 1
            else:
                pos = view.text_point(firstRow, 0)
                view.insert(edit, pos, "\n")
            lastRow += 1

            # check if there is 'else' in line after block
            after = view.text_point(lastRow + 2, 0)
            match = view.find(r"^\s*else", after)
            if match != None and match.begin() == after:
                line = view.line(view.text_point(lastRow + 1, 0))
                view.replace(edit, sublime.Region(line.end(), match.end()-4), " ")

            # add cursor position to list
            newRegions.append(sublime.Region(pos, pos))


        # set cursor position
        for region in newRegions:
            view.sel().add(region)

        # fix indendation of cursor position
        view.run_command("reindent", { "single_line": 1 })

