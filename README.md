# Zettle Sublime Text 3 Plugin

A [Sublime Text 3][sublime] plugin that supports Zettlekasten work flows.

If you are interested in more information on the Zettlekasten method check out https://zettelkasten.de/.

This is a personal project but I thought I would share it just in case someone else would find it useful. Feel free to raise issues if you see mistakes, have criticism, or have feature suggestions. This includes the documentation. I will respond if I have time :).

[sublime]: https://www.sublimetext.com/
[neuron]: https://neuron.zettel.page/
[obsidian]: https://obsidian.md/
[zettlr]: https://www.zettlr.com/
[pandoc]: https://pandoc.org

## Features

Once **Zettle** is installed and setup it supports these features:

 * Multiple different Zettlekasten directories with names and locations of your choice.
 * Creating a new zettle with a chronological unique ID in a Zettlekasten (if you have more than one, you can choose by name).
 * Auto-complete `[]()` common markdown links to other notes within the same Zettlekasten.
 * Auto-complete `[[]]` zettle links supported by [Neuron][neuron], [Obsidian][obsidian], and [Zettlr][zettlr].
 * Auto-complete `[[[]]]` folgezettle links supported by [Neuron][neuron].
 * Auto-complete `[@]` bibliographic citation tags supported by [Zettlr][zettlr] using an exported references file in the CSL JSON format.

## Motivation

### TLDR

I want to be able to:
 * take my notes in a form that is in plain text and widely supported
 * take my notes in a form that can be converted to most other forms simply. This allows me to communicate with the rest of the world.
 * edit my zettlekasten notes from within the text editor I usually have open
 * use convenient auto-completion for citations and linking notes
 * keep syntax consistent with other software that already exist so I have the option to use them to interact with my zettlekasten as well

**Zettle** adds creation of new notes in the zettlekasten from anywhere with a unique chronological ID and supports convenient auto-completion for linking notes and adding citations.

### Motivation In Detail

I spend most of my time within sublime text when I am working and reading papers. I prefer to take notes in markdown format to be able to take advantage of the plain text tooling ecosystem (for example version control). Markdown can also be converted to just about any format using [Pandoc][pandoc]. This allows me to send someone my notes and work in the format they prefer working with.

I have recently begun exploring the Zettlekasten method for a better way of storing my notes mostly out of curiosity but also because it removes the initial barrier to writing something down (determining how to organize and where to put it). The Zettlekasten allows you to separate that effort and add links or tags later when reading back through the notes. Organization grows organically over time (that's the idea anyway). Most importantly, there is software that supports the Zettlekasten system with powerful search functionality. This makes finding something in your collection of notes much easier. You could also take advantage of plain text recursive search tools such as [ripgrep](https://github.com/BurntSushi/ripgrep), if you prefer.

There are a few different software I started using to test the Zettlekasten method. Among them, [Zettlr][zettlr], [Obsidian][obsidian], [Neuron][neuron]. I love that [Zettlr][zettlr] supports bibliographic citations which are plain text readable (`[@bibtexid, 45]`), support page numbers, and are rendered. It supports math environments, inline math, and math rendering. And the math syntax uses the Latex syntax which is powerful, something I am already familiar with, and it can be copied into a Latex file when I am eventually writing a paper or technical report.

There was only a few things in [Zettlr][zettlr] that did not fit my work flow. The first, I already have a program that is open most of the time when I am working and reading (Sublime Text). I would prefer to not have to open another software for plain text editing just to take a note (again my opinion). Second, the text inserted when auto-completing a link has the form `[[1235634123]] expanded file name`. This does not work with any other piece of software that implements the Zettlekasten method. And if I were to change my mind later it would be much harder to write a script to change the syntax for all my files because the expanded file name cannot be distinguished from the paragraph it is in. Third, there is no support for normal markdown link auto-completion for linking zettles `[]()`. These are of course only my opinion and very specific to my personal taste.

I then took a look at [Obsidian][obsidian]. It has great search functionality different in some ways than [Zettlr][zettlr]. It find it feels slightly more snappy (personal speed preference). It keeps it simple and supports syntax highlighting of math and opening of pictures. However, math is not rendered in place and neither are pictures. It does not support citations but highlights the syntax. That was a big reason for not continuing to use this software as I write a decent amount of math in my notes and take notes on bibliographic references I have read.

Finally, I took a look at [Neuron][neuron]. It uses a server client model. The web server monitors the zettlekasten directory and rebuilds changed files for the website. The website supports searching by words, and tags. It shows back links (very useful), and folgezettle which I think are implemented in a cool way. Math rendering is supported. However, the search does not search through the content of the notes, only the title.

All of these software had really nice features. All interact with a folder of markdown files, but each have slightly different additional syntax to support the zettlekasten system. I developed this sublime text plugin to:

 * Augment the functionality of these software. Each software had unique features that I liked (citations, linking, folgezettle, back linking). Some could easily be supported within Sublime Text.
 * Keep the ability to add and edit notes with auto-completion in my text editor; the software I am usually using or already have open.
 * Support the common functionality of these software within sublime text. So when I need to use one of the software for its particular functionality or I want to change my work flow to a specific software I can.

## Manual Install

Currently the only way to install this plugin is manually. You can either copy this package and place it into Sublime Text's packages folder. To open the package directory open Sublime Text and use`Preferences > Browse Packages...` in the main menu. You can then copy the `zettle` folder into the package folder. Sublime Text should load the package automatically. You can check 

## Setup

Before the package works you have to define two settings. These must be placed in the `Zettle.sublime-settings` file in the `User` packages directory. You can open this file directly by using `Preferences > Package Settings > Zettle > Settings - User`. This option should be available once the installation is complete.

 * `zettle_named_directory_paths`: A dictionary / map of the Zettlekasten names to Zettlekasten absolute directory paths.
 * `zettle_references_file_path`: The absolute file path to the exported references from your reference management system of choice (Only tested with Zotero). The exported file must be in CSL JSON format. More info below.

You have to wrap the settings within valid JSON dictionary. For example the `Zettle.sublime-settings` I use is:

```json
{
    "zettle_named_directory_paths": {
        "Zettlekasten": "/home/franz/Documents/Notes/Zettlekasten",
    },
    "zettle_references_file_path": "/home/franz/Documents/Literature/references.json"
}
```

The `references.json` file of course does not exist yet so you need to create it. Place it where ever you like. I have mine in my literature folder. It must be in CSL JSON format. Each entry in the `references.json` file must have an `id` tag that is unique to that reference (for example `kaminski12DaysIce2010`). These can be generated in Zotero by installing [`Better BibTex`](https://retorque.re/zotero-better-bibtex/) for Zotero. Once installed in Zotero, highlight all your references, right-click, click `Export Items`, select `Better CSL JSON` and export to the file path you specified as the `zettle_references_file_path`.

Finally, markdown syntax does not have auto-complete enabled by default. Easiest way to change this is to open your markdown specific settings using `Preferences > Syntax Specific` in the main menu while having a `.md` file open. This opens `Markdown.sublime-settings` where you can add:

```json
{
    "auto_complete_triggers":
    [
        {
            "characters": "abcdefghijklmnopqrstuvwxyz",
            "selector": "text.html.markdown"
        }
    ],
    "extensions":
    [
        "markdown",
        "md"
    ],
    "spell_check": true,
}
```

The `auto_complete_triggers` setting enables auto-complete in the markdown file context. The `extensions` setting determines what file extensions that are considered to be of syntax `Markdown` when they are opened. The `spell_check` setting is not needed but greatly improves quality of life while writing notes.

**Note: The `Markdown` syntax does not support math blocks (`$$ $$`) or inline math(`$ $`) in its syntax highlighting among other things. The `Markdown Extended` syntax does so I usually prefer using that one. `Markdown Extended` syntax is part of the [Markdown Extended](https://packagecontrol.io/packages/Markdown%20Extended) package that can be installed using [Package Control](https://packagecontrol.io/).**

This completes the setup process.

## Workflow

Once you have completed installing and setting up the package you can start using it! To create a new zettle in your zettlekasten press `Ctrl+Shift+P` to open you command panel and begin typing `zettle`. You will see `Zettle: New Zettle` as one of the available commands. Select it and press `Enter`. This opens text dialog box at the bottom of the editor that is automatically populated with a unique chronological 14 digit id and the `.md` extension (for example `20201127172809 .md`). You can place your cursor after the id and name the zettle whatever you would like. Just remember that this file name is what will be shown later in the auto-complete menu when linking zettles.

When you press `Enter` a new file with that name will be created and opened in the current window. Now it is up to you to fill the zettle.

### Linking 

**Zettle** supports linking to other files in the same Zettlekasten with the `.md` extension. **Zettle**  does this by extending the auto-complete feature of Sublime Text. **Zettle** populates the auto-complete menu using the file names within the directory. There are two different types of links to files supported by **Zettle**.

 * `[[]]`: The auto-complete triggers when the first two brackets are typed in (`[[`). Now continue typing to search through the auto-complete drop-down menu. Press `Tab` to auto-complete. This syntax for linking is supported by [Neuron][neuron]. As is the triple square bracket (`[[[]]]`) syntax that represents Folgezettle in [Neuron][neuron]. The auto-complete inserts the file name without the extension. This syntax works with [Neuron][neuron], [Obsidian][obsidian], and triggers a general search in [Zettlr][zettlr].
 
 * `[]()`: The generic markdown link syntax is also supported. The auto-complete triggers on the `](`. When the link is inserted the spaces in the name are escaped as `%20`. This is because [Neuron's][neuron] web server does not play well with spaces in normal markdown links.

### Citations

**Zettle** uses the same citation syntax that [Zettlr][zettlr] uses. The syntax is `[@citationid]`. The auto-complete triggers after `[@`. A page number can be included in the citation using a comma, space, then a number within the citation (for example `[@citationid, 456]`). This does not mean anything to [Neuron][neuron] or [Obsidian][obsidian], but it will render as a reference in [Zettlr][zettlr].

### Searching

Sublime text supports the amazing **Search Anything** feature. So if you have the Zettlekasten folder open in Sublime Text you can search and open a specific note quickly using `Ctrl + P`.
